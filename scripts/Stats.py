import scipy.stats as scipy
import scikit_posthocs as scikit
import pandas as pd
import seaborn as sns
import numpy as np
import os

class Stats:
    def __init__(self):
        self.output_dir = r'C:\Users\Ashwin Sakhare\Google Drive\Projects\Data Science\Python\NCAAF\analysis'
        sns.set()

    def summary(self, data_df, response=None, predictor=None):
        if response is None:
            data_df = data_df.groupby([predictor]).size().to_frame('count')
            data_df[predictor] = data_df.index
            data_df = data_df.reset_index(drop=True)
            data_df = data_df[[predictor, 'count']]

            return data_df

        else:
            data_df[response] = pd.to_numeric(data_df[response], errors='coerce')

            data_df = data_df.groupby([predictor], as_index=False).\
                agg({response: ['mean', 'std', 'median', 'count']})

            data_df.columns = data_df.columns.get_level_values(0)
            data_df.columns = [predictor, 'mean', 'std', 'median', 'count']

            data_df[['mean', 'median', 'std']] = data_df[['mean', 'median', 'std']].astype(int)

            return data_df

    def kruskal_wallis(self, data_df, predictor, response):
        data_df[response] = pd.to_numeric(data_df[response], errors='coerce')

        kruskal_out = scipy.kruskal(*[group[response].values for name, group in data_df.groupby(predictor)])
        kruskal_df = pd.DataFrame([kruskal_out], columns=kruskal_out._fields)
        kruskal_df.columns = ['h-statistic', 'p-value']

        return kruskal_df

    def posthoc_dunn(self, data_df, predictor, response):
        data_df[response] = pd.to_numeric(data_df[response], errors='coerce')

        dunn_df = scikit.posthoc_dunn(data_df, val_col=response, group_col=predictor, p_adjust='bonferroni')
        dunn_df = dunn_df.applymap(lambda x: np.nan if x < 0 else x)
        dunn_df = dunn_df.round(2)
        dunn_df = dunn_df.applymap(lambda x: "< 0.001" if x < 0.001 else x)

        return dunn_df

    def shapiro_wilk(self, data_df, predictor, response):
        data_df[response] = pd.to_numeric(data_df[response], errors='coerce')

        data_df = data_df[[predictor,response]].groupby([predictor])

        shapiro_df = data_df.apply(
            lambda x: pd.Series(scipy.shapiro(x), index=['t-statistic', 'p-value']) if len(x) > 2
            else pd.Series([np.nan, np.nan], index=['t-statistic', 'p-value'])).reset_index()

        shapiro_df['t-statistic'] = shapiro_df['t-statistic'].round(2)
        shapiro_df['p-value'] = shapiro_df['p-value'].round(3)
        shapiro_df.loc[shapiro_df['p-value'] == 0, 'p-value'] = "< 0.001"

        return shapiro_df

    def recruiting_score(self, teams_df, coaches_df):
        for index, coach in coaches_df.iterrows():
            coach_rankings = teams_df[(teams_df['name'] == coach['team']) &
                                      (teams_df['year'] > coach['first_year']) &
                                      (teams_df['year'] <= (coach['last_year'] + 1))]

            coach_rankings = coach_rankings.reset_index(drop=True)
            coach_rankings['standardized'] = (teams_df[teams_df['name'] == coach['team']]['nat_rank'].mean()
                                              - coach_rankings['nat_rank']) \
                                             / teams_df[teams_df['name'] == coach['team']]['nat_rank'].std()

            coaches_df.loc[index, 'recruiting_ability'] = coach_rankings['standardized'].median()

        coaches_df = coaches_df.reset_index(drop=True)

        return coaches_df

    def development_score_by_draft_position(self, players_df, coaches_df, predictors, response):
        draft_positions = players_df.groupby(predictors, as_index=False).agg({response: ['mean', 'std']})
        mean_expected_response = 'mean_expected_' + response
        sd_expected_response = 'sd_expected_' + response
        draft_positions.columns = predictors + [mean_expected_response, sd_expected_response]

        for index, coach in coaches_df.iterrows():
            drafted_players = players_df[(players_df['team'] == coach['team']) &
                                         (players_df['drafted'] > coach['first_year']) &
                                         (players_df['drafted'] <= (coach['last_year']) + 1)]

            drafted_players = pd.merge(left=drafted_players, right=draft_positions, how='left',
                                       left_on=predictors, right_on=predictors)

            drafted_players = drafted_players.reset_index(drop=True)

            drafted_players['standardized'] = (drafted_players[mean_expected_response] - drafted_players[response]) \
                                              / drafted_players[sd_expected_response]

            if drafted_players.shape[0] > 5:
                coaches_df.loc[index, 'development_ability'] = drafted_players['standardized'].median()
            else:
                coaches_df.loc[index, 'development_ability'] = np.nan

        coaches_df = coaches_df.reset_index(drop=True)

        return coaches_df

    def development_score_by_draft_count(self, players_df, coaches_df):
        drafted = players_df[~players_df['drafted'].isnull()]
        drafted = drafted.groupby(['stars']).size()
        all = players_df.groupby(['stars']).size()

        drafted_fraction = pd.concat([drafted, all], axis=1)
        drafted_fraction.columns = ['drafted','total']
        drafted_fraction['stars'] = drafted_fraction.index
        drafted_fraction = drafted_fraction.reset_index(drop=True)
        drafted_fraction['fraction'] = drafted_fraction['drafted'] / drafted_fraction['total']

        drafted_fraction.to_csv(os.path.join(self.output_dir,'drafted_fraction_by_star.csv'))

        for index, coach in coaches_df.iterrows():
            players = players_df[(players_df['team'] == coach['team'])]
            cond1 = (players['drafted'] > coach['first_year']) & (players['drafted'] <= (coach['last_year']) + 1)
            cond2 = ((players['enrolled'] + players['ncaaf_years']) > coach['first_year']) & (players['enrolled'] <= (coach['last_year']))
            cond3 = ((players['enrolled'] + 4) > coach['first_year']) & (players['enrolled'] <= (coach['last_year']))
            players = players[cond1 | cond2 | cond3]

            coach_drafted = players[~players['drafted'].isnull()]
            coach_drafted = coach_drafted.groupby(['stars']).size()
            coach_all = players.groupby(['stars']).size()

            coach_drafted_fraction = pd.concat([coach_drafted, coach_all], axis=1)
            coach_drafted_fraction.columns = ['drafted', 'total']
            coach_drafted_fraction['stars'] = coach_drafted_fraction.index
            coach_drafted_fraction = coach_drafted_fraction.reset_index(drop=True)
            coach_drafted_fraction['fraction'] = coach_drafted_fraction['drafted'] / coach_drafted_fraction['total']
            coach_drafted_fraction = coach_drafted_fraction[['stars','drafted','total','fraction']]

            merged = pd.merge(left=coach_drafted_fraction, right=drafted_fraction, how='left',
                                       left_on='stars', right_on='stars')

            merged = merged.dropna(subset=['total_x'])
            merged = merged[merged['total_x'] >= 5]
            merged['fraction_x'] = merged['fraction_x'].fillna(0)

            perc_diff = (merged['fraction_x'] - merged['fraction_y']) / (merged['fraction_y']) * 100

            coaches_df.loc[index, 'development_ability'] = perc_diff.median()

        coaches_df = coaches_df.dropna(subset=['development_ability'])

        coaches_df = coaches_df.reset_index(drop=True)

        coaches_df['development_ability'] = coaches_df['development_ability'] + \
                                            coaches_df['development_ability'].min() * -1 + .01

        coaches_df['development_ability'] = coaches_df['development_ability'].transform(lambda x: scipy.boxcox(x)[0])

        mean_percent_drafted = coaches_df['development_ability'].mean()
        std_percent_drafted = coaches_df['development_ability'].std()
        coaches_df['development_ability'] = (coaches_df['development_ability'] - mean_percent_drafted) / std_percent_drafted
        coaches_df = coaches_df.reset_index(drop=True)

        return coaches_df

    def box_cox(self, data_df, group, attribute):
        data_df[attribute] = data_df.groupby(group)[attribute].transform(lambda x: scipy.boxcox(x)[0])

        return data_df

    def normalize(self, coaches_df, attribute):
        coaches_df[attribute] = (coaches_df[attribute] - coaches_df[attribute].min()) \
                                / (coaches_df[attribute].max() - coaches_df[attribute].min()) - .5

        return coaches_df

