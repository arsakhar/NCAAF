from scripts.Player import Player
from scripts.Logger import Logger
from scripts.Sports247 import Sports247
from scripts.SportsReference import SportsReference
from scripts.ProFootballReference import ProFootballReference
from scripts.FootballDatabase import FootballDatabase
from scripts.ChunkGenerator import ChunkGenerator
from multiprocessing import Pool

import pandas as pd
import itertools
import os

class PlayerController:
    def __init__(self):
        self.data_dir = r'C:\Users\Ashwin Sakhare\Google Drive\Projects\Data Science\Python\NCAAF\data'
        self.ranking_cutoff = 5000
        self.start_year = 2000
        self.end_year = 2020
        self.max_eligible_years = 6

    def get_players(self, players_df=None):
        if players_df is None:
            players = self.find_players()

            return players

        players_df = players_df.reset_index(drop=True)
        players = []
        for index, row in players_df.iterrows():
            player = Player()
            player.id = row['id']
            player.name = row['name']
            player.team = row['team']
            player.position_side = row['position_side']
            player.position_group = row['position_group']
            player.position = row['position']
            player.metrics = row['metrics']
            player.overall_rank = row['overall_rank']
            player.pos_rank = row['pos_rank']
            player.state_rank = row['state_rank']
            player.nat_rank = row['nat_rank']
            player.stars = row['stars']
            player.score = row['score']
            player.enrolled = row['enrolled']
            player.transferred = row['transferred']
            player.ncaaf_status = row['ncaaf_status']
            player.ncaaf_years = row['ncaaf_years']
            player.drafted = row['drafted']
            player.round = row['round']
            player.pick = row['pick']
            player.nfl_position = row['nfl_position']

            players.append(player)

            print('{}\r'.format(index), end="")

        return players

    def get_players_df(self, players=None):
        if players is None:
            file_name = 'Players.csv'
            data_path = os.path.join(self.data_dir, file_name)
            players_df = pd.read_csv(data_path, dtype=str, na_filter= False)

            return players_df

        data = [[]]
        for player in players:
            data.append([player.id,
                         player.name,
                         player.team,
                         player.position_side,
                         player.position_group,
                         player.position,
                         player.metrics,
                         player.overall_rank,
                         player.pos_rank,
                         player.state_rank,
                         player.nat_rank,
                         player.stars,
                         player.score,
                         player.enrolled,
                         player.transferred,
                         player.ncaaf_status,
                         player.ncaaf_years,
                         player.drafted,
                         player.round,
                         player.pick,
                         player.nfl_position])

        players_df = pd.DataFrame(data, columns=['id',
                                                 'name',
                                                 'team',
                                                 'position_side',
                                                 'position_group',
                                                 'position',
                                                 'metrics',
                                                 'overall_rank',
                                                 'pos_rank',
                                                 'state_rank',
                                                 'nat_rank',
                                                 'stars',
                                                 'score',
                                                 'enrolled',
                                                 'transferred',
                                                 'ncaaf_status',
                                                 'ncaaf_years',
                                                 'drafted',
                                                 'round',
                                                 'pick',
                                                 'nfl_position'])

        players_df = players_df.loc[1:]
        players_df['overall_rank'] = pd.to_numeric(players_df['overall_rank'], errors='coerce')
        players_df['enrolled'] = pd.to_numeric(players_df['enrolled'], errors='coerce')
        players_df = players_df.sort_values(by=['enrolled', 'overall_rank', 'score', 'pos_rank', 'state_rank'])
        players_df = players_df.reset_index(drop=True)

        return players_df

    def save_players(self, players):
        players_df = self.get_players_df(players)
        file_name = 'Players.csv'
        data_path = os.path.join(self.data_dir, file_name)
        players_df.to_csv(data_path, index=False)

    def update_players(self, players):
        Logger().log("PlayerController: starting update player query")

        footballdatabase = FootballDatabase(self.max_eligible_years)
        sportsreference = SportsReference(self.max_eligible_years)
        profootballreference = ProFootballReference()

        subset_list = []
        for i in range(0, len(players), 500):
            subset = players[i:i + 500]

            subset = sportsreference.get_ncaaf_career(subset)
            subset = footballdatabase.get_ncaaf_career(subset)
            subset = profootballreference.get_draft_info(subset)

            subset_list.append(subset)

        players = list(itertools.chain.from_iterable(subset_list))

        Logger().log("PlayerController: finished update player query")

        return players

    def find_players(self):
        sports247 = Sports247()
        footballdatabase = FootballDatabase(self.max_eligible_years)
        sportsreference = SportsReference(self.max_eligible_years)
        profootballreference = ProFootballReference()

        players_list = []

        for index, year in enumerate(range(self.start_year, self.end_year + 1)):
            Logger().log("PlayerController: starting player query for " + str(year))

            players = sports247.get_player_rankings(year, year, self.ranking_cutoff)
            players = sportsreference.get_ncaaf_career(players)
            players = footballdatabase.get_ncaaf_career(players)
            players = profootballreference.get_draft_info(players)

            players_df = self.get_players_df(players)

            if index == 0:
                players_df.to_csv('Players_temp.csv', index=False)

            else:
                players_df.to_csv('Players_temp.csv', mode='a', header=False, index=False)

            players_list.append(players)

            Logger().log("PlayerController: finished player query for " + str(year))

        players = list(itertools.chain.from_iterable(players_list))

        for index, player in enumerate(players):
            player.id = str(index)
            try:
                player.position_side = Player().position_sides[player.position]
                player.position_group = Player().position_groups[player.position]
            except:
                player.position_side = ''
                player.position_group = ''

        return players
