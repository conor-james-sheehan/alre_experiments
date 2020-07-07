from typing import Dict, List, Sequence

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.figure import Figure
from pandas.core.generic import NDFrame

from experiments.mixtures_parameterized.mp_analysis import TEST_STAT_ABBRV_STR, THETA_STR
from util.plotting import plot_line_graph_with_errors


def plot_mle_error(mle_err) -> Figure:
    fig, ax = plt.subplots()
    mean = mle_err.mean(axis=1, level=1)
    stderr = mle_err.sem(axis=1, level=1)
    plot_line_graph_with_errors(mean=mean, stderr=stderr, ax=ax)
    ax.set(title='MAE on MLE estimate')
    return fig


def get_test_stat(nllrs: List[pd.DataFrame]) -> List[pd.DataFrame]:
    return [2*(nllr.subtract(nllr.min(), axis=1)) for nllr in nllrs]


def plot_total_mse(ucb_test_stat: List[pd.DataFrame], random_test_stat: List[pd.DataFrame]) -> Figure:

    def _get_total_mse(test_stats):
        squared_error = [(ts.subtract(ts['Exact'], axis=0) ** 2).drop('Exact', axis=1).mean(axis=0)
                         for ts in test_stats]
        squared_error = pd.concat(squared_error, axis=1, keys=range(len(squared_error)))
        return squared_error

    ucb_mse = _get_total_mse(ucb_test_stat)
    random_mse = _get_total_mse(random_test_stat)
    mse = pd.concat([ucb_mse, random_mse], axis=1, keys=['UCB', 'Random']).reset_index(drop=True)
    mean = mse.mean(axis=1, level=0)
    stderr = mse.sem(axis=1, level=0)
    fig, ax = plt.subplots()
    plot_line_graph_with_errors(mean=mean, stderr=stderr, ax=ax)
    ax.set(title='Total MSE', xlabel='Active learning iteration')
    return fig


def plot_final_iteration_test_stat(ucb_test_stat: List[pd.DataFrame], random_test_stat: List[pd.DataFrame]) -> Figure:
    alpha = 0.2
    fig, axarr = plt.subplots(2)
    for ax, test_stat, name in zip(axarr, [ucb_test_stat, random_test_stat], ['UCB', 'Random']):
        n = len(test_stat)
        exact_test_stat = pd.concat([ts.iloc[:, -1] for ts in test_stat], axis=1, keys=range(n))
        test_stat = pd.concat([ts.iloc[:, -2] for ts in test_stat], axis=1, keys=range(n))
        exact_test_stat.plot(color='b', label=None, alpha=alpha, ax=ax)
        test_stat.plot(color='r', label=None, alpha=alpha, ax=ax)
        ax.legend().set_visible(False)
        ax.set_ylabel(TEST_STAT_ABBRV_STR, rotation=90, labelpad=5)
        ax.set(title=name)
    axarr[-1].set(xlabel=THETA_STR)
    return fig


def _plot_debug_graph(
        ucb_nllr: pd.DataFrame,
        ucb_std: pd.DataFrame,
        iterations: Sequence[int]
):
    fig, axarr = plt.subplots(len(iterations), figsize=(10, len(iterations)*2.5))
    for ax, iteration in zip(np.ravel(axarr), iterations):
        column = f'Iteration {iteration}'
        plot_line_graph_with_errors(
            mean=ucb_nllr[column].to_frame(),
            stderr=ucb_std[column].to_frame(),
            ax=ax
        )
        ucb_nllr['Exact'].plot(ax=ax, color='r', label='Exact')
    return fig


def analyse_mixtures_active_learning(results: Dict[str, List[NDFrame]], config: Dict):
    mle = results['mle']
    ucb_nllr = results['ucb_nllr']
    random_nllr = results['random_nllr']

    mle_err = pd.concat(
        [df.subtract(df['Exact'], axis=0).drop('Exact', axis=1) for df in mle],
        axis=1,
        keys=range(len(mle))
    ).abs()
    mle_err_fig = plot_mle_error(mle_err)

    ucb_test_stat = get_test_stat(ucb_nllr)
    random_test_stat = get_test_stat(random_nllr)

    mse_fig = plot_total_mse(ucb_test_stat=ucb_test_stat, random_test_stat=random_test_stat)

    test_stat_fig = plot_final_iteration_test_stat(ucb_test_stat=ucb_test_stat, random_test_stat=random_test_stat)

    figures = dict(
        mle_err=mle_err_fig,
        mse=mse_fig,
        test_stat=test_stat_fig
    )

    return figures
