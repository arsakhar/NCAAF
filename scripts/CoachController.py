from scripts.Coach import Coach
from scripts.Logger import Logger
import pandas as pd
import os


class CoachController:
    def __init__(self):
        self.data_dir = r'C:\Users\Ashwin Sakhare\Google Drive\Projects\Data Science\Python\NCAAF\data'
        self.tables_dir = r'C:\Users\Ashwin Sakhare\Google Drive\Projects\Data Science\Python\NCAAF\tables'

    def find_coaches(self):
        file_name = 'Football_Coaches.csv'
        data_path = os.path.join(self.tables_dir, file_name)
        football_coaches_df = pd.read_csv(data_path, sep=',', dtype=str)

        coaches = []
        for index in range(len(football_coaches_df)):
            for column in football_coaches_df.columns[1:]:
                if int(column) < 2000:
                    continue

                coach = Coach()

                coach.name = self.trim(football_coaches_df.loc[index, column])
                coach.team = self.trim(football_coaches_df.loc[index, 'FBS Team'])
                coach.year = self.trim(column)

                if coach.name != "No Team":
                    coaches.append(coach)

        for index, coach in enumerate(coaches):
            coach.id = str(index)

        return coaches

    def add_recruiting(self, coaches, teams):
        for coach in coaches:
            for team in teams:
                if coach.team == team.name:
                    if coach.year == team.year:
                        coach.three_star = team.three_star
                        coach.four_star = team.four_star
                        coach.five_star = team.five_star
                        coach.points = team.points
                        coach.avg = team.avg
                        coach.nat_rank = team.nat_rank

        return coaches

    def add_drafted(self, coaches, players):
        for coach in coaches:
            drafted = 0
            for player in players:
                if coach.team == player.team:
                    if coach.year == player.drafted:
                        drafted += 1

            coach.drafted = drafted

        return coaches

    def save_coaches(self, coaches):
        coaches_df = self.get_coaches_df(coaches)
        file_name = 'Coaches.csv'
        data_path = os.path.join(self.data_dir, file_name)
        coaches_df.to_csv(data_path, index=False)

    def get_coaches(self, coaches_df=None):
        if coaches_df is None:
            coaches = self.find_coaches()

            return coaches

        coaches_df = coaches_df.reset_index(drop=True)
        coach_ids = coaches_df['id'].to_list()

        coaches = []
        for coach_id in coach_ids:
            coach = Coach()
            coach.id = str(coach_id)
            coach.name = coaches_df.loc[coaches_df['id'] == coach_id]['name']
            coach.name = str(self.get_attribute_value(coach.name))

            if coach.name == "":
                Logger().log("Coach: more than 1 row found for player id. skipping coach")
                continue

            coach.team = coaches_df.loc[coaches_df['id'] == coach_id]['team']
            coach.team = str(self.get_attribute_value(coach.team))

            coach.year = coaches_df.loc[coaches_df['id'] == coach_id]['year']
            coach.year = str(self.get_attribute_value(coach.year))

            coach.three_star = coaches_df.loc[coaches_df['id'] == coach_id]['three_star']
            coach.three_star = str(self.get_attribute_value(coach.three_star))

            coach.four_star = coaches_df.loc[coaches_df['id'] == coach_id]['four_star']
            coach.four_star = str(self.get_attribute_value(coach.four_star))

            coach.five_star = coaches_df.loc[coaches_df['id'] == coach_id]['five_star']
            coach.five_star = str(self.get_attribute_value(coach.five_star))

            coach.avg = coaches_df.loc[coaches_df['id'] == coach_id]['avg']
            coach.avg = str(self.get_attribute_value(coach.avg))

            coach.points = coaches_df.loc[coaches_df['id'] == coach_id]['points']
            coach.points = str(self.get_attribute_value(coach.points))

            coach.nat_rank = coaches_df.loc[coaches_df['id'] == coach_id]['nat_rank']
            coach.nat_rank = str(self.get_attribute_value(coach.nat_rank))

            coach.drafted = coaches_df.loc[coaches_df['id'] == coach_id]['drafted']
            coach.drafted = str(self.get_attribute_value(coach.drafted))

            coaches.append(coach)

        return coaches

    def get_coaches_df(self, coaches=None):
        if coaches is None:
            file_name = 'Coaches.csv'
            data_path = os.path.join(self.data_dir, file_name)
            coaches_df = pd.read_csv(data_path, dtype=str, na_filter= False)

            return coaches_df

        data = [[]]
        for coach in coaches:
            data.append([coach.id,
                         coach.name,
                         coach.team,
                         coach.year,
                         coach.three_star,
                         coach.four_star,
                         coach.five_star,
                         coach.avg,
                         coach.points,
                         coach.nat_rank,
                         coach.drafted])

        coaches_df = pd.DataFrame(data, columns=['id',
                                                 'name',
                                                 'team',
                                                 'year',
                                                 'three_star',
                                                 'four_star',
                                                 'five_star',
                                                 'avg',
                                                 'points',
                                                 'nat_rank',
                                                 'drafted'])

        coaches_df = coaches_df.loc[1:]
        coaches_df['year'] = pd.to_numeric(coaches_df['year'], errors='coerce')
        coaches_df['nat_rank'] = pd.to_numeric(coaches_df['nat_rank'], errors='coerce')
        coaches_df = coaches_df.sort_values(by=['year', 'nat_rank', 'avg'])
        coaches_df = coaches_df.reset_index(drop=True)

        return coaches_df

    def get_attribute_value(self, attribute):
        if len(attribute) == 1:
            return attribute.values[0]
        else:
            return ""

    def trim(self, string):
        return string.strip()
