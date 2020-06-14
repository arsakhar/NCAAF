import grequests

from scripts.Team import Team
from scripts.WebRequests import WebRequests
from scripts.Logger import Logger
from scripts.ChunkGenerator import ChunkGenerator
from scripts.Player import Player

import re
from datetime import date
from bs4 import BeautifulSoup as soup
import requests
from multiprocessing import Pool
import itertools
import time


class FootballDatabase:
    def __init__(self, _max_eligible_years):
        self.max_eligible_years = _max_eligible_years
        self.request_header = WebRequests().request_header
        self.request_timeout = WebRequests().request_timeout

    def get_ncaaf_career(self, players):
        query_start_time = time.perf_counter()
        player_chunks,num_chunks = ChunkGenerator().generate_data_chunks(players)
        pool = Pool(processes=num_chunks)
        players = pool.map(self.get_data_chunks, player_chunks)
        pool.close()
        players = list(itertools.chain.from_iterable(players))

        query_end_time = time.perf_counter()
        Logger().log_query_time("FootballDB: career query completed in ", query_start_time, query_end_time)

        return players

    def get_data_chunks(self, players):
        for index, player in enumerate(players):
            if (player.ncaaf_years != '') or (int(float(player.enrolled)) < 2009):
                continue

            team = player.team
            team = Team().get_local_name(team, 'FootballDB')

            enrolled_year = int(float(player.enrolled))

            player_url = self.find_player_url(player, team, enrolled_year)
            players[index] = self.add_stats(player, player_url)

        return players

    def find_player_url(self, player, team, enrolled_year):
        curr_year = int(date.today().year)
        eligible_years = list(range(enrolled_year, enrolled_year + self.max_eligible_years))
        eligible_years = [x for x in eligible_years if x <= curr_year]

        request_urls = []
        for eligible_year in eligible_years:
            request_url = 'https://www.footballdb.com/college-football/teams/fbs/' \
                         + str(team) \
                         + '/roster/' \
                         + str(eligible_year)

            request_urls.append(request_url)

        try:
            responses = grequests.map(
                (grequests.get(u, headers=self.request_header, timeout=self.request_timeout) for u in request_urls),
                size=len(request_urls))
        except:
            Logger().log("FootballDB: Unable to query some/all urls for "
                         + player.name
                         + " | "
                         + team
                         + " | "
                         + ', '.join(map(str, eligible_years))
                         + ', '.join(map(str, request_urls)))

            player_url = ''
            return player_url

        responses = [response for response in responses if response is not None]

        for response in responses:
            page_html = response.text
            page_soup = soup(page_html, "lxml")

            if page_soup is None:
                Logger().log("FootballDB: " + "no html page returned")
                continue

            roster_list = page_soup.find("div", {"class": "divtable divtable-striped divtable-mobile"})
            roster_list = roster_list.findAll("a", href=re.compile(r"/college-football/players/")) if roster_list else []

            for roster_item in roster_list:
                roster_player = roster_item.get_text() if roster_item else ""
                roster_player = " ".join(roster_player.split(",")[::-1])
                roster_player = Player().trim_name(roster_player)

                player_of_interest = Player().trim_name(player.name)

                if player_of_interest == roster_player:
                    player_url = 'https://www.footballdb.com' + roster_item['href']
                    return player_url

        player_url = ''
        return player_url

    def add_stats(self, player, player_url):
        if not player_url:
            Logger().log("FootballDB: "
                         + "Unable to find "
                         + player.name
                         + " | "
                         + player.team
                         + " | "
                         + player.enrolled
                         + " | "
                         + player_url)
            return player

        try:
            response = requests.get(url=player_url, headers=self.request_header, timeout=self.request_timeout)
        except:
            Logger().log("FootballDB: Unable to get web query for "
                         + player.name
                         + " | "
                         + player_url)

            return player

        if response is None:
            Logger().log("FootballDB: " + "No query response for " + player.name + " | " + player_url)
            return player

        page_html = response.text
        page_soup = soup(page_html, "lxml")

        if page_soup is None:
            Logger().log("FootballDB: " + "No html page returned for " + player.name + " | " + player_url)
            return player

        stats_list = page_soup.find("table", {"class": "statistics scrollable"})
        stats_list = stats_list.find("tbody") if stats_list else []
        stats_list = stats_list.findAll("tr", re.compile(r"row")) if stats_list else []

        if not stats_list:
            Logger().log("FootballDB: " + "No stats found for " + player.name + " | " + player_url)
            return player

        enrolled_years = []
        teams = []

        for stats_item in stats_list:
            playing_year = stats_item.find("td", {"class": "center"})
            playing_year = playing_year.get_text() if playing_year else ""

            team = stats_item.find("a", href=re.compile(r"/college-football/teams/fbs/"))
            team = team['href'] if team else ""
            team = team.replace("/college-football/teams/fbs/", "")
            team = Team().get_global_name(team, 'FootballDB')

            if not team:
                team = stats_item.find("span", {"class": "hidden-xs"})
                team = team.get_text() if team else ""
                team = re.sub("\(.*\)|\s-\s.*", "", team).strip()

            enrolled_years.append(playing_year)
            teams.append(team)

        if not all(x == teams[0] for x in teams):
            player.transferred = self.trim(teams[-1])

        player.ncaaf_years = self.trim(str(len(enrolled_years)))

        last_enrolled_year = int(enrolled_years[-1])
        curr_year = int(date.today().year)

        if last_enrolled_year < curr_year:
            player.ncaaf_status = "exhausted"
        else:
            player.ncaaf_status = "active"

        return player

    def trim(self, string):
        return string.strip()