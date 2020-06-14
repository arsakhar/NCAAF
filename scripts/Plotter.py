import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from adjustText import adjust_text
import statsmodels.api as sm


class Plotter:
    def __init__(self):
        self.file_suffix = ''
        sns.set()
        sns.set_context("paper")

    def sns_boxplot(self, data_df, predictor, response):
        data_df[response] = pd.to_numeric(data_df[response], errors='coerce')
        data_df = data_df.groupby([predictor]).filter(lambda x: len(x) > 1)

        plt.cla()
        plt.clf()
        plt.figure(figsize=(10, 8))

        sns.set_style('darkgrid', {'axes.linewidth': 1, 'axes.edgecolor': 'black'})
        sns.boxplot(x=predictor, y=response, data=data_df)
        ax  = plt.gca()
        ax.tick_params(axis='both', labelsize=16)

        return plt

    def qq_plot(self, data_df, predictor, response):
        data_df[response] = pd.to_numeric(data_df[response], errors='coerce')
        data_df = data_df.groupby([predictor]).filter(lambda x: len(x) > 1)

        levels = data_df[predictor].unique().tolist()
        rows, columns = self.get_fig_size(len(levels))

        plt.cla()
        plt.clf()
        plt.figure(figsize=(8, 8))

        for index, level in enumerate(levels):
            ax = plt.subplot(rows, columns, index + 1)
            sm.qqplot(data_df[data_df[predictor] == level][response], line='s', ax=ax)
            plt.title(level, weight='bold')

            if index > 0:
                plt.xlabel('')
                plt.ylabel('')

        plt.tight_layout()

        return plt

    def sns_scatter(self, data_df, predictor, response, h_size=None, w_size=None):
        data_df[predictor] = pd.to_numeric(data_df[predictor], errors='coerce')
        data_df[response] = pd.to_numeric(data_df[response], errors='coerce')

        plt.clf()
        if (h_size is not None) & (w_size is not None):
            plt.figure(figsize=(h_size, w_size))

        sns.set_style('darkgrid', {'axes.linewidth': 1, 'axes.edgecolor': 'black'})
        sns.scatterplot(x=predictor, y=response, data=data_df, s=40)

        return plt

    def label_points(self, data_df, predictor, response, label):
        a = pd.concat({'x': data_df[predictor],
                       'y': data_df[response],
                       'val': data_df[label]}, axis=1)

        annotations = []
        for i, point in a.iterrows():
            annotations.append(plt.text(point['x'], point['y'], str(point['val']), size=14))

        adjust_text(annotations)

    def sns_distplot(self, data_df, predictor=None, response=None):
        if predictor is None:
            plt.cla()
            plt.clf()
            plt.figure(figsize=(8, 8))
            ax = plt.gca()
            ax.tick_params(axis='both', labelsize=16)
            sns.set_style('darkgrid', {'axes.linewidth': 1, 'axes.edgecolor': 'black'})
            sns.distplot(data_df[response])

            return plt

        else:
            levels = data_df[predictor].unique().tolist()
            rows, columns = self.get_fig_size(len(levels))

            plt.cla()
            plt.clf()
            plt.figure(figsize=(8, 8))

            for index, level in enumerate(levels):
                ax = plt.subplot(rows, columns, index + 1)
                sns.distplot(data_df[data_df[predictor] == level][response])
                plt.title(level, weight='bold')
                self.set_labels(plt, response.capitalize(), "Probability Density Function")
                if index > 0:
                    plt.xlabel('')
                    plt.ylabel('')

            plt.tight_layout()

            return plt


    def set_labels(self, plt, x_label=None, y_label=None, font_size=None):
        if x_label is not None:
            if font_size is not None:
                plt.xlabel(x_label, fontsize=font_size)
            else:
                plt.xlabel(x_label)

        if y_label is not None:
            if font_size is not None:
                plt.ylabel(y_label, fontsize=font_size)
            else:
                plt.ylabel(y_label)

        return plt

    def set_title(self, plt, title, font_size=None):
        if font_size is not None:
            plt.suptitle(title, weight='bold', fontsize = font_size)

        else:
            plt.suptitle(title, weight='bold')

        return plt

    def get_fig_size(self, num_plots):
        if num_plots <= 4:
            rows, columns = 2, 2
        elif num_plots <= 9:
            rows, columns = 3, 3
        else:
            rows, columns = 4,3

        return rows, columns