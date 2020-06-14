from scripts.Team import Team
from scripts.Logger import Logger
from scripts.Sports247 import Sports247

import pandas as pd
import itertools
import os


class TeamController:
    def __init__(self):
        self.data_dir = r'C:\Users\Ashwin Sakhare\Google Drive\Projects\Data Science\Python\NCAAF\data'
        self.ranking_cutoff = 300
        self.start_year = 2000
        self.end_year = 2020

    def get_teams(self, teams_df=None):
        if teams_df is None:
            teams = self.find_teams()

            return teams

        teams_df = teams_df.reset_index(drop=True)
        team_ids = teams_df['id'].to_list()

        players = []
        for team_id in team_ids:
            team = Team()
            team.id = str(team_id)
            team.name = teams_df.loc[teams_df['id'] == team_id]['name']
            team.name = str(self.get_attribute_value(team.name))

            if team.name == "":
                Logger().log("Player: more than 1 row found for player id. skipping player")
                continue

            team.conference = teams_df.loc[teams_df['id'] == team_id]['conference']
            team.conference = str(self.get_attribute_value(team.conference))

            team.commits = teams_df.loc[teams_df['id'] == team_id]['commits']
            team.commits = str(self.get_attribute_value(team.commits))

            team.year = teams_df.loc[teams_df['id'] == team_id]['year']
            team.year = str(self.get_attribute_value(team.year))

            team.nat_rank = teams_df.loc[teams_df['id'] == team_id]['nat_rank']
            team.nat_rank = str(self.get_attribute_value(team.nat_rank))

            team.five_star = teams_df.loc[teams_df['id'] == team_id]['five_star']
            team.five_star = str(self.get_attribute_value(team.five_star))

            team.four_star = teams_df.loc[teams_df['id'] == team_id]['four_star']
            team.four_star = str(self.get_attribute_value(team.four_star))

            team.three_star = teams_df.loc[teams_df['id'] == team_id]['three_star']
            team.three_star = str(self.get_attribute_value(team.three_star))

            team.avg = teams_df.loc[teams_df['id'] == team_id]['avg']
            team.avg = str(self.get_attribute_value(team.avg))

            team.points = teams_df.loc[teams_df['id'] == team_id]['points']
            team.points = str(self.get_attribute_value(team.points))

            players.append(team)

        return players

    def save_teams(self, teams):
        teams_df = self.get_teams_df(teams)
        file_name = 'Teams.csv'
        data_path = os.path.join(self.data_dir, file_name)
        teams_df.to_csv(data_path, index=False)

    def get_teams_df(self, teams=None):
        if teams is None:
            file_name = 'Teams.csv'
            data_path = os.path.join(self.data_dir, file_name)
            teams_df = pd.read_csv(data_path, dtype=str, na_filter= False)

            return teams_df

        data = [[]]
        for team in teams:
            data.append([team.id,
                         team.name,
                         team.conference,
                         team.nat_rank,
                         team.commits,
                         team.five_star,
                         team.four_star,
                         team.three_star,
                         team.avg,
                         team.points,
                         team.year])

        teams_df = pd.DataFrame(data, columns=['id',
                                               'name',
                                               'conference',
                                               'nat_rank',
                                               'commits',
                                               'five_star',
                                               'four_star',
                                               'three_star',
                                               'avg',
                                               'points',
                                               'year'])

        teams_df = teams_df.loc[1:]
        teams_df['nat_rank'] = pd.to_numeric(teams_df['nat_rank'], errors='coerce')
        teams_df['year'] = pd.to_numeric(teams_df['year'], errors='coerce')
        teams_df = teams_df.sort_values(by=['year', 'nat_rank', 'points'])
        teams_df = teams_df.reset_index(drop=True)

        return teams_df

    def find_teams(self):
        sports247 = Sports247()

        teams_list = []

        for index, year in enumerate(range(self.start_year, self.end_year + 1)):
            Logger().log("TeamController: starting team query for " + str(year))

            teams = sports247.get_team_rankings(year, year, self.ranking_cutoff)

            teams_df = self.get_teams_df(teams)

            if index == 0:
                teams_df.to_csv('Teams_temp.csv', mode='a', index=False)

            else:
                teams_df.to_csv('Teams_temp.csv', mode='a', header=False, index=False)

            teams_list.append(teams)

            Logger().log("TeamController: finished team query for " + str(year))

        teams = list(itertools.chain.from_iterable(teams_list))

        teams = sports247.add_conferences(teams)

        for index, team in enumerate(teams):
            team.id = str(index)

        return teams

    def get_attribute_value(self, attribute):
        if len(attribute) == 1:
            return attribute.values[0]
        else:
            return ""

