import pandas as pd
import re
import os


class Team:
    def __init__(self):
        self.tables_dir = r'C:\Users\Ashwin Sakhare\Google Drive\Projects\Data Science\Python\NCAAF\tables'

        self.id: str = ''
        self.name: str = ''
        self.conference: str = ''
        self.year: str = ''
        self.nat_rank: str = ''
        self.commits: str = ''
        self.five_star: str = ''
        self.four_star: str = ''
        self.three_star: str = ''
        self.avg: str = ''
        self.points: str = ''

        file_name = 'Team_Conversion_Table.csv'
        data_path = os.path.join(self.tables_dir, file_name)
        self.table = pd.read_csv(data_path)

    def trim_name(self, name):
        name = re.sub(r"[^a-zA-Z]+", ' ', name)
        name = name.lower().strip()

        possible_suffix = name.split(' ')[-1]
        suffixes_to_remove = ['ii', 'iii', 'jr', 'sr']
        if possible_suffix in suffixes_to_remove:
            components = name.split(' ')
            name = ''
            for component in components[:-1]:
                name = name + ' ' + component

        name = name.replace(' ', '')

        return name

    def get_global_name(self, team, website):
        team = team.lower().strip()
        team_index = self.table[self.table[website] == team][website].index.tolist()

        team = self.table.loc[team_index[0], 'Global'] if len(team_index) == 1 else ""

        return team

    def get_local_name(self, team, website):
        team_index = self.table.Global[self.table.Global == team].index.tolist()
        team = self.table.loc[team_index[0], website] if len(team_index) == 1 else ""

        return team