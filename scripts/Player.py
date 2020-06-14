import re


class Player:
    def __init__(self):
        self.id: str = ''
        self.name: str = ''
        self.position_side: str = ''
        self.position_group: str = ''
        self.position: str = ''
        self.metrics: str = ''
        self.overall_rank: str = ''
        self.pos_rank: str = ''
        self.state_rank: str = ''
        self.nat_rank: str = ''
        self.stars: str = ''
        self.score: str = ''
        self.team: str = ''
        self.enrolled: str = ''
        self.transferred: str = ''
        self.ncaaf_status: str = ''
        self.ncaaf_years: str = ''
        self.drafted: str = ''
        self.round: str = ''
        self.pick: str = ''
        self.nfl_position: str = ''

        self.position_groups = {
            "OLB": "LB", "ILB": "LB",
            "DT": "DL", "WDE": "DL", "SDE": "DL",
            "S": "DB", "CB": "DB",
            "OG": "OL", "OT": "OL", "OC": "OL",
            "DUAL": "QB", "PRO": "QB",
            "TE": "TE",
            "RB": "RB", "APB": "RB", "SF": "RB",
            "ATH": "ATH",
            "WR": "WR",
            "K": "ST", "LS": "ST", "P": "ST", "RET": "ST",
            "FB": "FB"}

        self.position_sides = {
            "OLB": "Def", "ILB": "Def", "DT": "Def", "WDE": "Def",
            "SDE": "Def", "S": "Def", "CB": "Def",
            "OG": "Off", "OT": "Off", "OC": "Off", "DUAL": "Off",
            "FB": "Off", "APB": "Off", "PRO": "Off", "TE": "Off",
            "RB": "Off", "WR": "Off", "ATH": "Off", "SF": "Off",
            "K": "ST", "LS": "ST", "P": "ST", "RET": "ST"}

    def trim_name(self, name):
        name = re.sub(r"[^a-zA-Z]+", ' ', name)
        # name = re.sub(r"[^a-zA-Z0-9]+", ' ', name)
        # name = ''.join([i for i in name if not i.isdigit()])
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
