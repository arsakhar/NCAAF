from scripts.Plotter import Plotter
from scripts.Stats import Stats

import os
import numpy as np
import pandas as pd

class Analysis:
    def __init__(self):
        self.output_dir = r'C:\Users\Ashwin Sakhare\Google Drive\Projects\Data Science\Python\NCAAF\analysis'

    def check_scraping(self, players_df):
        plotter = Plotter()
        stats = Stats()

        predictor = 'enrolled'
        input_df = self.remove_empty_rows(players_df, [predictor])

        out_df = stats.summary(input_df, predictor=predictor)
        out_df.to_csv(os.path.join(self.output_dir, 'summary_' + predictor + '_by_year.csv'), index=False)

        plt = plotter.sns_scatter(out_df, predictor, 'count')
        plt = plotter.set_labels(plt, "Recruiting Year", "Count")
        plt = plotter.set_title(plt, "High School Recruits in 247 Sports Database")
        plt.xticks(np.arange(min(out_df[predictor]), max(out_df[predictor]) + 1, 2.0))
        plt.savefig(os.path.join(self.output_dir+ '\scatterplots', 'scatter_' + predictor + '_by_year.png'))

        predictor = 'drafted'
        response = 'pick'

        input_df = self.remove_empty_rows(players_df, [predictor, response])

        out_df = stats.summary(input_df, predictor=predictor, response=response)
        out_df.to_csv(os.path.join(self.output_dir, 'summary_ ' + predictor + '_by_year.csv'), index=False)

        plt = plotter.sns_scatter(out_df, predictor, 'count')
        plt = plotter.set_labels(plt, "Draft Year", "Count")
        plt = plotter.set_title(plt, "College Players Drafted From 247 Sports Database")
        plt.xticks(np.arange(min(out_df[predictor]), max(out_df[predictor]) + 1, 2.0))
        plt.savefig(os.path.join(self.output_dir + '\scatterplots', 'scatter_' + predictor + '_by_year.png'))

    def pre_process_teams_for_ranking_analysis(self, teams_df):
        response = 'nat_rank'
        predictor = 'name'
        p5_conferences = ['SEC', 'ACC', 'Pac-12', 'Big-12', 'Big-Ten']

        teams_df = teams_df[teams_df['conference'].isin(p5_conferences)]
        teams_df = self.remove_empty_rows(teams_df, [predictor, response] + ['year'])
        teams_df = self.remove_non_numeric_rows(teams_df, [response] + ['year'])
        teams_df = self.to_numeric(teams_df, [response] + ['year'])

        plotter = Plotter()
        teams = teams_df[predictor].unique().tolist()

        for team in teams:
            team_df = teams_df[teams_df[predictor] == team]

            plt = plotter.sns_distplot(team_df, predictor = None, response = response)
            plt = plotter.set_labels(plt, "National Rank", "Probability Density Function", 18)
            plt = plotter.set_title(plt, team, 18)
            plt.savefig(os.path.join(self.output_dir + '\histograms', 'dist_plot_' + team + '.png'))

        stats = Stats()
        teams_df = stats.box_cox(teams_df, predictor, response)

        teams = teams_df[predictor].unique().tolist()

        for team in teams:
            team_df = teams_df[teams_df[predictor] == team]

            plt = plotter.sns_distplot(team_df, predictor = None, response = response)
            plt = plotter.set_labels(plt, "National Rank", "Probability Density Function", 18)
            plt = plotter.set_title(plt, team, 18)
            plt.savefig(os.path.join(self.output_dir + '\histograms', 'dist_plot_' + 'box_cox_' + team + '.png'))

        return teams_df

    def pre_process_players_for_draft_position_analysis(self, players_df):
        plotter = Plotter()
        stats = Stats()

        predictors = ['stars', 'position_group']
        response = 'pick'

        indexes = players_df[players_df['stars'] == '3'].index
        names = ['3-', '3', '3+']
        players_df = self.remove_empty_rows(players_df, ['enrolled'])
        players_df = self.to_numeric(players_df, ['score','enrolled'])
        players_df = players_df.sort_values(by=['enrolled','score'], ascending=[True, False])

        players_df = players_df.reset_index(drop=True)

        players_df.loc[indexes, 'stars'] = pd.qcut(players_df.loc[indexes, 'score'], 3, labels=names)

        players_df = players_df[players_df['transferred'] == '']
        players_df = self.remove_empty_rows(players_df, predictors + [response])
        players_df = self.remove_non_numeric_rows(players_df, [response])
        players_df = self.to_numeric(players_df, [response] + ['drafted'])

        players_df = players_df.reset_index(drop=True)

        for predictor in predictors:
            plt = plotter.sns_boxplot(players_df, predictor, response)
            plt = plotter.set_labels(plt, predictor.replace('_',' ').title(), 'Draft Position', 18)
            if predictor == 'stars':
                plt = plotter.set_title(plt, "Draft Position based on Star Rating", 18)
            else:
                plt = plotter.set_title(plt, "Draft Position based on Position Group", 18)

            plt.savefig(os.path.join(self.output_dir + '\\boxplots', 'boxplot_' + response + '_by_' + predictor + '.png'))

            out_df = stats.summary(players_df, predictor=predictor, response=response)
            out_df.to_csv(os.path.join(self.output_dir, 'summary_' + response + '_by_' + predictor + '.csv'),
                          index=False)

            plt = plotter.sns_distplot(players_df, predictor, response)
            plt.savefig(os.path.join(self.output_dir + '\histograms', 'dist_plot_' + predictor + '.png'))

            plt = plotter.qq_plot(players_df, predictor, response)
            plt.savefig(
                os.path.join(self.output_dir + '\qqplots', 'qqplot_' + response + '_by_' + predictor + '.png'))

            out_df = stats.shapiro_wilk(players_df, predictor=predictor, response=response)
            out_df.to_csv(os.path.join(self.output_dir, 'shapiro_wilk_' + response + '_by_' + predictor + '.csv'),
                          index=False)

        for predictor in predictors:
            out_df = stats.kruskal_wallis(players_df, predictor=predictor, response=response)
            out_df.to_csv(os.path.join(self.output_dir, 'kurskal_wallis_' + response + '_by_' + predictor + '.csv'),
                          index=False)

            out_df = stats.posthoc_dunn(players_df, predictor=predictor, response=response)
            out_df.to_csv(os.path.join(self.output_dir, 'posthoc_dunn_' + response + '_by_' + predictor + '.csv'))

        predictor = 'stars'

        players_df = stats.box_cox(players_df, predictor, response)

        plt = plotter.sns_distplot(players_df, predictor, response)
        plt.savefig(os.path.join(self.output_dir + '\histograms', 'dist_plot_' + 'box_cox_' + predictor + '.png'))

        plt = plotter.qq_plot(players_df, predictor, response)
        plt.savefig(
            os.path.join(self.output_dir + '\qqplots', 'qqplot_' + 'boxcox_' + response + '_by_' + predictor + '.png'))

        return players_df

    def pre_process_players_for_draft_count_analysis(self, players_df):
        players_df['ncaaf_status'] = ''
        indexes = players_df[players_df['stars'] == '3'].index
        names = ['3-', '3', '3+']
        players_df = self.remove_empty_rows(players_df, ['enrolled'])
        players_df = self.to_numeric(players_df, ['score','enrolled', 'ncaaf_years'])
        players_df = players_df.sort_values(by=['enrolled','score'], ascending=[True, False])

        players_df = players_df.reset_index(drop=True)

        players_df.loc[indexes, 'stars'] = pd.qcut(players_df.loc[indexes, 'score'], 3, labels=names)

        players_df = self.to_numeric(players_df, ['drafted'])
        indexes = players_df[players_df['enrolled'] < 2016].index
        players_df.loc[indexes,'ncaaf_status'] = 'exhausted'

        indexes = players_df[~players_df['drafted'].isnull()].index
        players_df.loc[indexes,'ncaaf_status'] = 'exhausted'

        players_df = players_df[players_df['transferred'] == '']
        players_df = players_df[players_df['ncaaf_status'] == 'exhausted']

        players_df = players_df.reset_index(drop=True)

        return players_df

    def development_vs_recruiting(self, coaches_df, teams_df, players_df):
        coaches_df = pd.merge(left=coaches_df, right=teams_df[['name','conference']], how='left', left_on='team',
                               right_on='name')

        coaches_df.drop('name_y', axis=1, inplace=True)
        coaches_df = coaches_df.rename(columns={'name_x': 'name'})
        coaches_df = coaches_df.groupby(['name', 'team'], as_index=False).agg(
            {'conference': 'first',
             'year': ["min", "max"]})

        coaches_df.columns = coaches_df.columns.get_level_values(0)
        coaches_df.columns = ['name', 'team', 'conference', 'first_year', 'last_year']
        coaches_df[['first_year', 'last_year']] = coaches_df[['first_year', 'last_year']].astype(int)
        # coaches_df = coaches_df[coaches_df['last_year'] - coaches_df['first_year'] >= 4].reset_index(drop=True)
        coaches_df = coaches_df[coaches_df['last_year'] >= 2019].reset_index(drop=True)

        stats = Stats()
        coaches_df = stats.recruiting_score(teams_df, coaches_df)
        recruiting_ability = 'recruiting_ability'

        coaches_df = stats.development_score_by_draft_position(players_df, coaches_df,
                                                               ['stars'],
                                                               'pick')

        development_ability = 'development_ability'

        coaches_df = self.remove_nan_rows(coaches_df, [development_ability, recruiting_ability])

        plotter = Plotter()
        plt = plotter.sns_scatter(coaches_df, recruiting_ability, development_ability, 18.5, 10.5)
        plotter.label_points(coaches_df, recruiting_ability, development_ability, 'name')

        plt.xlabel("Recruiting", fontsize=20)
        plt.ylabel("Player Development (Draft Position)", fontsize=20)
        plt.axvline(x=0, color='black')
        plt.axhline(y=0, color='black')
        plt.tick_params(axis="x", labelsize=18)
        plt.tick_params(axis="y", labelsize=18)
        plt.suptitle('Player Development and Recruiting - Active P5 Coaches', fontweight="bold", fontsize=20)
        plt.savefig(os.path.join(self.output_dir + '\scatterplots', 'scatter_development_by_recruiting.png'))

        p5_conferences = ['SEC', 'ACC', 'Pac-12', 'Big-12', 'Big-Ten']

        for conference in p5_conferences:
            subset_df = coaches_df[coaches_df['conference'] == conference].reset_index(drop=True)

            plt = plotter.sns_scatter(subset_df, recruiting_ability, development_ability, 18.5, 10.5)
            plotter.label_points(subset_df, recruiting_ability, development_ability, 'name')

            plt.xlabel("Recruiting", fontsize=20)
            plt.ylabel("Player Development", fontsize=20)
            plt.axvline(x=0, color='black')
            plt.axhline(y=0, color='black')
            plt.tick_params(axis="x", labelsize=18)
            plt.tick_params(axis="y", labelsize=18)
            plt.suptitle('Player Development and Recruiting - Active P5 Coaches - ' + conference, fontweight="bold", fontsize=20)
            plt.savefig(os.path.join(self.output_dir + '\scatterplots', 'scatter_development_by_recruiting - '
                                     + conference + '.png'))

    def percent_drafted_vs_draft_position(self, coaches_df, teams_df, players_df):
        stats = Stats()

        coaches_df = pd.merge(left=coaches_df, right=teams_df[['name', 'conference']], how='left', left_on='team',
                              right_on='name')

        coaches_df.drop('name_y', axis=1, inplace=True)
        coaches_df = coaches_df.rename(columns={'name_x': 'name'})
        coaches_df = coaches_df.groupby(['name', 'team'], as_index=False).agg(
            {'conference': 'first',
             'year': ["min", "max"]})

        coaches_df.columns = coaches_df.columns.get_level_values(0)
        coaches_df.columns = ['name', 'team', 'conference', 'first_year', 'last_year']
        coaches_df[['first_year', 'last_year']] = coaches_df[['first_year', 'last_year']].astype(int)
        # coaches_df = coaches_df[coaches_df['last_year'] - coaches_df['first_year'] >= 4].reset_index(drop=True)
        coaches_df = coaches_df[coaches_df['last_year'] >= 2019].reset_index(drop=True)

        players_1_df = self.pre_process_players_for_draft_position_analysis(players_df)

        coaches_1_df = stats.development_score_by_draft_position(players_1_df, coaches_df,
                                                               ['stars'],
                                                               'pick')

        coaches_1_df = self.remove_nan_rows(coaches_1_df, ['development_ability']).reset_index(drop=True)

        players_2_df = self.pre_process_players_for_draft_count_analysis(players_df)

        coaches_2_df = coaches_df[coaches_df['name'].isin(coaches_1_df['name'].to_list())].reset_index(drop=True)
        coaches_2_df = stats.development_score_by_draft_count(players_2_df, coaches_2_df)

        coaches_1_df = coaches_1_df[coaches_1_df['name'].isin(coaches_2_df['name'].to_list())].reset_index(drop=True)

        merged = pd.merge(left=coaches_1_df, right=coaches_2_df, how='left',
                          left_on=['name','team','first_year','last_year'],
                          right_on=['name','team','first_year','last_year'])

        draft_score = 'development_ability_x'
        percent_drafted = 'development_ability_y'

        merged = self.remove_nan_rows(merged, [percent_drafted, draft_score])

        plotter = Plotter()
        plt = plotter.sns_scatter(merged, percent_drafted, draft_score, 18.5, 10.5)
        plotter.label_points(merged, percent_drafted, draft_score, 'name')

        plt.xlabel("Drafted Players (%)", fontsize=20)
        plt.ylabel("Draft Position", fontsize=20)
        plt.axvline(x=0, color='black')
        plt.axhline(y=0, color='black')
        plt.tick_params(axis="x", labelsize=18)
        plt.tick_params(axis="y", labelsize=18)
        plt.suptitle('Player Development - Active P5 Coaches', fontweight="bold", fontsize=20)
        plt.savefig(os.path.join(self.output_dir + '\scatterplots', 'scatter_perc_drafted_by_draft_position.png'))

    def remove_empty_rows(self, data_df, columns):
        for column in columns:
            data_df = data_df[data_df[column] != ''].reset_index(drop=True)

        for column in columns:
            data_df = data_df.groupby(column).filter(lambda x: len(x) > 1).reset_index(drop=True)

        return data_df

    def remove_non_numeric_rows(self, data_df, columns):
        for column in columns:
            data_df = data_df[data_df[column].apply(lambda x: x.isnumeric())]

        return data_df

    def remove_nan_rows(self, data_df, columns):
        data_df[columns] = data_df[columns].apply(pd.to_numeric, errors='coerce', axis=1)
        data_df = data_df.replace(-np.Inf, np.nan)
        data_df = data_df.replace(np.Inf, np.nan)
        data_df = data_df.dropna(subset=columns)

        return data_df

    def to_numeric(self, data_df, columns):
        data_df[columns] = data_df[columns].apply(pd.to_numeric, errors='coerce', axis=1)

        return data_df
