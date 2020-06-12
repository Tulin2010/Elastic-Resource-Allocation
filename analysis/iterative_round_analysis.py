"""Analysis of results generated by the iterative round testing script"""

from __future__ import annotations

import json
from typing import List, Iterable

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from src.core.core import decode_filename, save_plot, analysis_filename, ImageFormat

matplotlib.rcParams['font.family'] = 'monospace'


def plot_price_rounds(encoded_filenames: List[str], x_axis: str, title: str,
                      save_formats: Iterable[ImageFormat] = ()):
    """
    Plots the price round graphs

    :param encoded_filenames: The list of encoded filenames
    :param x_axis: The x axis on the plot
    :param title: The title of the plot
    :param save_formats: The save image format list
    """
    data = []
    test_name: str = ''
    model_names: List[str] = []

    for encoded_filename in encoded_filenames:
        filename, model_name, test_name = decode_filename('paper', encoded_filename)
        model_names.append(model_name)

        with open(filename) as file:
            file_data = json.load(file)
            for pos, model_result in enumerate(file_data):
                for name, result in model_result.items():
                    data.append([pos, model_name, name, result['initial_cost'], result['price change'],
                                 result['total_iterations'], result['total_messages'], result['total money'],
                                 result['solve_time'], result['sum value']])

    df = pd.DataFrame(data, columns=['Pos', 'Model Name', 'Algorithm Name', 'Initial cost', 'Price Change',
                                     'Total Iterations', 'Total Messages', 'Total Money', 'Solve Time', 'Sum Value'])
    g = sns.FacetGrid(df, col='Model Name', sharex=False, margin_titles=True, height=4)
    # noinspection PyUnresolvedReferences
    (g.map(sns.barplot, x_axis, 'Algorithm Name').set_titles('{col_name}'))

    for pos, model in enumerate(model_names):
        values = [np.mean(df[(df['Model Name'] == model) & (df['Algorithm Name'] == algo)][x_axis])
                  for algo in df['Algorithm Name'].unique()]
        g.axes[0, pos].set_xlim(min(values) * 0.97, max(values) * 1.02)

    g.fig.subplots_adjust(top=0.88)
    g.fig.suptitle(title)

    save_plot(analysis_filename(test_name, x_axis), 'iterative_round', image_formats=save_formats)
    plt.show()


if __name__ == "__main__":

    september_20 = [
        'iterative_round_results_basic_j12_s2_0',
        'iterative_round_results_basic_j15_s2_0',
        'iterative_round_results_basic_j15_s3_0',
        'iterative_round_results_basic_j25_s5_0'
    ]

    paper = [
        'round_num_fog_j15_s3_0'
    ]

    for attribute in ['Total Iterations', 'Total Messages', 'Total Money', 'Solve Time', 'Sum Value']:
        plot_price_rounds(paper, attribute, f'{attribute} of basic model',
                          save_formats=[ImageFormat.EPS, ImageFormat.PNG])
    # plot_price_rounds(september_20, 'Sum Value', '{} of basic model'.format('Sum Value'), save_formats=[ImageFormat.EPS, ImageFormat.PNG])
