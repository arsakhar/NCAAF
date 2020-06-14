import re


class Coach:
    def __init__(self):
        self.id: str = ''
        self.name: str = ''
        self.team: str = ''
        self.year: str = ''
        self.three_star: str = ''
        self.four_star: str = ''
        self.five_star: str = ''
        self.avg: str = ''
        self.points: str = ''
        self.nat_rank: str = ''
        self.drafted: str = ''

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



