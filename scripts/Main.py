from scripts.PlayerController import PlayerController
from scripts.TeamController import TeamController
from scripts.CoachController import CoachController
from scripts.Analysis import Analysis

if __name__ == '__main__':
    PlayerController = PlayerController()
    TeamController = TeamController()
    CoachController = CoachController()
    Analysis = Analysis()

    # players_df = PlayerController.get_players_df()
    # players = PlayerController.get_players(players_df)
    #
    # players = PlayerController.update_players(players)
    #
    # PlayerController.save_players(players)

    players_df = PlayerController.get_players_df()
    teams_df = TeamController.get_teams_df()
    coaches_df = CoachController.get_coaches_df()

    teams_df = Analysis.pre_process_teams_for_ranking_analysis(teams_df)
    Analysis.check_scraping(players_df)
    players_df = Analysis.pre_process_players_for_draft_position_analysis(players_df)
    Analysis.development_vs_recruiting(coaches_df, teams_df, players_df)

    players_df = PlayerController.get_players_df()
    teams_df = TeamController.get_teams_df()
    coaches_df = CoachController.get_coaches_df()

    teams_df = Analysis.pre_process_teams_for_ranking_analysis(teams_df)
    Analysis.percent_drafted_vs_draft_position(coaches_df, teams_df, players_df)