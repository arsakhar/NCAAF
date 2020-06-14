from scripts.WebRequests import WebRequests
from scripts.Player import Player
from scripts.Logger import Logger
from scripts.Team import Team
from scripts.ChunkGenerator import ChunkGenerator

from bs4 import BeautifulSoup as soup
import requests
from multiprocessing import Pool
import time
import itertools


class ProFootballReference:
    def __init__(self):
        self.request_header = WebRequests().request_header
        self.request_timeout = WebRequests().request_timeout

    def get_draft_info(self, players):
        query_start_time = time.perf_counter()
        player_chunks, num_chunks = ChunkGenerator().generate_data_chunks(players)
        pool = Pool(processes=num_chunks)
        players = pool.map(self.get_data_chunks, player_chunks)
        pool.close()
        players = list(itertools.chain.from_iterable(players))

        query_end_time = time.perf_counter()
        Logger().log_query_time("ProFootballReference: draft query completed in ", query_start_time, query_end_time)

        return players

    def get_data_chunks(self, players):
        for index, player in enumerate(players):
            if player.drafted != '':
                continue

            if player.transferred != '':
                team = player.transferred
            else:
                team = player.team

            team = Team().get_local_name(team, 'ProFootballReference')

            players[index] = self.add_stats(player, team)

        return players

    def add_stats(self, player, team):
        team_url = 'https://www.pro-football-reference.com/schools/' + team + '/drafted.htm'

        try:
            response = requests.get(url=team_url, headers=self.request_header, timeout=self.request_timeout)
        except:
            Logger().log("ProFootballReference: Unable to query "
                         + team
                         + " for "
                         + player.name
                         + " | "
                         + team_url)

            return player

        if response is None:
            Logger().log("ProFootballReference: No query response for "
                         + team
                         + " for "
                         + player.name
                         + " | "
                         + team_url)
            return player

        page_html = response.text
        page_soup = soup(page_html, "lxml")

        if page_soup is None:
            Logger().log("ProFootballReference: " + "No html page returned for " + team_url)
            return player

        drafted_list = page_soup.find("tbody")
        drafted_list = drafted_list.findAll("tr") if drafted_list else []

        if not drafted_list:
            Logger().log("ProFootballReference: " + "No draft list for " + player.team)
            return player

        for drafted_item in drafted_list:
            drafted_player = drafted_item.find("td", {"data-stat": "player"}).find("a")
            drafted_player = drafted_player.get_text() if drafted_player else ""
            drafted_player = Player().trim_name(drafted_player)

            drafted_year = drafted_item.find("td", {"data-stat": "year_id"}).find("a")
            drafted_year = drafted_year.get_text() if drafted_year else ""
            drafted_year = int(drafted_year)

            player_of_interest = Player().trim_name(player.name)

            enrolled_year = int(float(player.enrolled))

            if (player_of_interest == drafted_player) and (drafted_year >= enrolled_year):
                stats = []
                stat_list = drafted_item.findAll("td")
                stat_list = stat_list if stat_list else []

                for stat in stat_list:
                    stats.append(stat.get_text())

                stats = stats[:-1]

                player.drafted = self.trim(stats[0])
                player.round = self.trim(stats[2])
                player.pick = self.trim(stats[3])
                player.nfl_position = self.trim(stats[6])

        return player

    def trim(self, string):
        return string.strip()