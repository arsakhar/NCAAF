import grequests

from scripts.Team import Team
from scripts.WebRequests import WebRequests
from scripts.ChunkGenerator import ChunkGenerator
from scripts.Logger import Logger

from bs4 import BeautifulSoup as soup
import math
import re
import itertools
from multiprocessing import Pool
from scripts.Player import Player
import time
import requests


class Sports247:
    def __init__(self):
        self.request_header = WebRequests().request_header
        self.request_timeout = WebRequests().request_timeout

    def get_request_responses(self, start_year, end_year, cutoff, core_url, page_url, suffix_url):
        years = list(range(start_year, end_year + 1))
        pages = list((range(1, math.ceil(cutoff / 50) + 1)))

        request_urls = []
        for year in years:
            for page in pages:
                request_url = core_url \
                      + str(year) \
                      + page_url \
                      + str(page) \
                      + suffix_url

                request_urls.append(request_url)

        try:
            responses = grequests.map(
                (grequests.get(u, headers=self.request_header, timeout=self.request_timeout) for u in request_urls),
                size=len(request_urls))
        except:
            Logger().log("Sports247: Unable to query some/all urls for "
                         + ', '.join(map(str, pages))
                         + " | "
                         + ', '.join(map(str, years)))

        responses = [response for response in responses if response is not None]

        return responses


    def get_player_rankings(self, start_year, end_year, cutoff):
        query_start_time = time.perf_counter()

        core_url = 'https://247sports.com/Season/'
        page_url = '-Football/CompositeRecruitRankings/?ViewPath' \
                   '=~%2FViews%2FSkyNet%2FPlayerSportRanking%2F_SimpleSetForSeason.ascx&InstitutionGroup' \
                   '=HighSchool&Page='
        suffix_url = '&_=1576263470372'

        responses = self.get_request_responses(start_year, end_year, cutoff, core_url, page_url, suffix_url)
        response_chunks, num_chunks = ChunkGenerator().generate_response_chunks(responses)
        pool = Pool(processes=num_chunks)

        players = pool.map(self.get_player_chunk, response_chunks)
        pool.close()
        players = list(itertools.chain.from_iterable(players))

        query_end_time = time.perf_counter()
        Logger().log_query_time("Sports247: player rankings query completed in ", query_start_time, query_end_time)

        return players

    def get_player_chunk(self, responses_chunk):
        players = []

        for response in responses_chunk:
            page_html = response.text
            page_soup = soup(page_html, "lxml")

            if page_soup is None:
                Logger().log("Sports247: " + "No html page returned")
                continue

            enrolled = page_soup.find("title", text=re.compile("Top Football Recruits"))
            enrolled = enrolled.get_text().strip().split(' ')[0] if enrolled else ""

            rankings_list = page_soup.findAll(
                lambda tag: tag.name == 'li' and tag.get('class') == ['rankings-page__list-item'])

            for rankings_entry in rankings_list:
                player = Player()

                player.name = rankings_entry.find("a", {"class": "rankings-page__name-link"})
                player.name = self.trim(player.name.get_text()) if player.name else ""

                player.position = rankings_entry.find("div", {"class": "position"})
                player.position = self.trim(player.position.get_text()) if player.position else ""

                player.metrics = rankings_entry.find("div", {"class": "metrics"})
                player.metrics = self.trim(player.metrics.get_text()) if player.metrics else ""

                player.overall_rank = rankings_entry.find("div", {"class": "primary"})
                player.overall_rank = self.trim(player.overall_rank.get_text()) if player.overall_rank else ""

                player.pos_rank = rankings_entry.find("a", {"class": "posrank"})
                player.pos_rank = self.trim(player.pos_rank.get_text()) if player.pos_rank else ""

                player.state_rank = rankings_entry.find("a", {"class": "sttrank"})
                player.state_rank = self.trim(player.state_rank.get_text()) if player.state_rank else ""

                player.nat_rank = rankings_entry.find("a", {"class": "natrank"})
                player.nat_rank = self.trim(player.nat_rank.get_text()) if player.nat_rank else ""

                player.stars = rankings_entry.findAll("span", {"class": "icon-starsolid yellow"})
                player.stars = self.trim(str(len(player.stars))) if player.stars else ""

                player.score = rankings_entry.find("span", {"class": "score"})
                player.score = self.trim(player.score.get_text()) if player.score else ""

                player.team = rankings_entry.find("div", {"class": "status"}).find("img", title=True)
                player.team = Team().get_global_name(player.team['title'],'Sports247') if player.team else ""
                player.team = self.trim(player.team)

                player.enrolled = self.trim(enrolled)

                players.append(player)

        return players

    def get_team_rankings(self, start_year, end_year, cutoff):
        query_start_time = time.perf_counter()

        core_url = 'https://247sports.com/Season/'
        page_url = '-Football/CompositeTeamRankings/?page='
        suffix_url = ''

        responses = self.get_request_responses(start_year, end_year, cutoff, core_url, page_url, suffix_url)

        response_chunks, num_chunks = ChunkGenerator().generate_response_chunks(responses)
        pool = Pool(processes=num_chunks)

        teams = pool.map(self.get_team_chunk, response_chunks)
        pool.close()
        teams = list(itertools.chain.from_iterable(teams))

        query_end_time = time.perf_counter()

        Logger().log_query_time("Sports247: team rankings query completed in ", query_start_time, query_end_time)

        return teams

    def get_team_chunk(self, responses_chunk):
        teams = []

        for response in responses_chunk:
            page_html = response.text
            page_soup = soup(page_html, "lxml")

            if page_soup is None:
                Logger().log("Sports247: " + "No html page returned")
                continue

            year = page_soup.find("title", text=re.compile("Football Team Rankings"))
            year = year.get_text().strip().split(' ')[0] if year else ""

            rankings_list = page_soup.findAll("li", {"class": "rankings-page__list-item"})

            for rankings_entry in rankings_list:
                team = Team()

                team.name = rankings_entry.div.find("div", {"class": "team"})
                team.name = self.trim(team.name.get_text()) if team.name else ""

                team.nat_rank = rankings_entry.div.find("div", {"class": "primary"})
                team.nat_rank = self.trim(team.nat_rank.get_text()) if team.nat_rank else ""

                team.avg = rankings_entry.div.find("div", {"class": "avg"})
                team.avg = self.trim(team.avg.get_text()) if team.avg else ""

                team.points = rankings_entry.div.find("div", {"class": "points"})
                team.points = self.trim(team.points.get_text()) if team.points else ""

                team.commits = rankings_entry.div.find("div", {"class": "total"})
                team.commits = team.commits.get_text() if team.commits else ""
                team.commits = self.trim(team.commits.strip().split(' ')[0]) if team.commits else ""

                stars_list = rankings_entry.div.find("ul", {"class": "star-commits-list"})
                stars_list = stars_list.findAll("li") if stars_list else []

                for stars_entry in stars_list:
                    if stars_entry.find("h2", string="3-Star"):
                        team.three_star = stars_entry.find("div")
                        team.three_star = self.trim(team.three_star.get_text()) if team.three_star else ""

                    if stars_entry.find("h2", string="4-Star"):
                        team.four_star = stars_entry.find("div")
                        team.four_star = self.trim(team.four_star.get_text()) if team.four_star else ""

                    if stars_entry.find("h2", string="5-Star"):
                        team.five_star = stars_entry.find("div")
                        team.five_star = self.trim(team.five_star.get_text()) if team.five_star else ""

                team.year = self.trim(year)

                teams.append(team)

        return teams

    def add_conferences(self, teams):
        teams_url = 'https://247sports.com/Season/2020-Football/CompositeTeamRankings/'

        try:
            response = requests.get(url=teams_url, headers=self.request_header, timeout=self.request_timeout)
        except:
            Logger().log("Sports247: Unable to get web query for teams")

            return teams

        page_html = response.text
        page_soup = soup(page_html, "lxml")

        if page_soup is None:
            Logger().log("Sports247: " + "No html page returned")

            return teams

        conferences_list = page_soup.find("ul", {"class": "rankings-page__conference-list"})
        conferences_list = conferences_list.findAll("a", href=re.compile(r"Conference")) if conferences_list else []

        conference_dictionary = {}

        for conferences_item in conferences_list:
            conference = conferences_item.get_text()
            conference_url = 'https://247sports.com' + conferences_item['href']

            conference_dictionary[conference] = conference_url

        for conference, conference_url in conference_dictionary.items():
            try:
                response = requests.get(url=conference_url, headers=self.request_header, timeout=self.request_timeout)
            except:
                Logger().log("Sports247: Unable to get web query for conference")

                continue

            page_html = response.text
            page_soup = soup(page_html, "lxml")

            if page_soup is None:
                Logger().log("Sports247: " + "No html page returned")
                continue

            rankings_list = page_soup.findAll("li", {"class": "rankings-page__list-item"})

            for team in teams:
                for rankings_entry in rankings_list:
                    conference_team = rankings_entry.div.find("div", {"class": "team"})
                    conference_team = self.trim(conference_team.get_text()) if conference_team else ""

                    if team.name == conference_team:
                        team.conference = self.trim(conference)

                        break

        return teams

    def trim(self, string):
        return string.strip()
