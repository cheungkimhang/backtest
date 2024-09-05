from typing import Tuple
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter

class visualization:
    
    def __init__(self):
        variable = None
    
    def generate_heatmap(self, sharpe_table: np.ndarray, calmar_table: np.ndarray, 
                         n_trade_table: np.ndarray, long_short_duration_ratio_table: np.ndarray,
                         xticklabels: np.ndarray, yticklabels: np.ndarray, 
                         xlabel: str, ylabel: str) -> plt.Figure:
        sns.set_theme(style="whitegrid")
        fig, ax = plt.subplots(ncols=2, nrows=2, figsize=(26, 13))

        sns.heatmap(sharpe_table.round(2), vmin=-2, vmax=3.5, ax=ax[0,0], cmap="coolwarm_r", annot=True, center=1, fmt='.2f', annot_kws={'size': 10}, xticklabels=xticklabels, yticklabels=yticklabels)
        ax[0,0].set_title(f'Sharpe ratio heatmap', fontsize=12)
        ax[0,0].set_ylabel(ylabel)
        ax[0,0].set_xlabel(xlabel)

        sns.heatmap(calmar_table.round(2), vmin=0, vmax=10, ax=ax[0,1], cmap="coolwarm_r", annot=True, center=2, fmt='.2f', annot_kws={'size': 10}, xticklabels=xticklabels, yticklabels=yticklabels)
        ax[0,1].set_title(f'Calmar ratio heatmap', fontsize=12)
        ax[0,1].set_ylabel(ylabel)
        ax[0,1].set_xlabel(xlabel)

        sns.heatmap(n_trade_table.round(2), vmin=0, vmax=2000, ax=ax[1,0], cmap="coolwarm_r", annot=True, center=800, fmt='.2f', annot_kws={'size': 10}, xticklabels=xticklabels, yticklabels=yticklabels)
        ax[1,0].set_title(f'No. of trades heatmap', fontsize=12)
        ax[1,0].set_ylabel(ylabel)
        ax[1,0].set_xlabel(xlabel)

        sns.heatmap(long_short_duration_ratio_table.round(2), vmin=0, vmax=2, ax=ax[1,1], cmap="coolwarm_r", annot=True, center=1.5, fmt='.2f', annot_kws={'size': 10}, xticklabels=xticklabels, yticklabels=yticklabels)
        ax[1,1].set_title(f'Long Short Duration Ratio heatmap', fontsize=12)
        ax[1,1].set_ylabel(ylabel)
        ax[1,1].set_xlabel(xlabel)

        fig.tight_layout()
        
        #plt.show()

        return fig

    def generate_equity_curve(self, df: pd.DataFrame, title: str, ylabel: str, xlabel: str) -> plt.Figure:
        fig, ax = plt.subplots(figsize=(12, 8))

        # Plot both series on the same y-axis
        ax.plot(df["timestamps"], df["cum_pnl"], color='red', label="Strategy Cumulative PnL")
        ax.plot(df["timestamps"], df["underlying_cumu"], color='black', label="Buy-and-Hold Cumulative PnL")

        ax.set_ylabel(ylabel)
        ax.set_xlabel(xlabel)

        unique_timestamps = df["timestamps"].unique()
        tick_indices = [i for i, x in enumerate(df["timestamps"]) if x in unique_timestamps]

        num_ticks = 5
        tick_step = max(1, len(tick_indices) // (num_ticks - 1))
        tick_indices = tick_indices[::tick_step]

        ax.set_xticks(df["timestamps"].iloc[tick_indices])
        ax.set_xticklabels(df["timestamps"].iloc[tick_indices], rotation=45)

        plt.title(title)

        ax.legend(loc='upper left')

        # plt.show()

        return fig

    def bband_visualization(self, df: pd.DataFrame, title: str, ylabel: str, xlabel: str) -> plt.Figure:

        fig, ax = plt.subplots(figsize=(12, 8))

        ax.plot(df['timestamps'], df["variables"], color='red', label=ylabel)
        ax.plot(df['timestamps'], df['sma'], color='blue', label='Middle Band')
        ax.plot(df['timestamps'], df['upper_band'], color='black', label='Upper Band')
        ax.plot(df['timestamps'], df['lower_band'], color='black', label='Lower Band')

        ax2 = ax.twinx()
        ax2.bar(df['timestamps'], df['prices'], color='r', alpha=0.5, width=0.2)
        ax2.set_ylabel('Price (USD)', color='r')
        ax2.tick_params('y', colors='r')
        ax2.format_ydata = lambda x: f'${x:.2f}'
        ax2.yaxis.set_major_formatter(FormatStrFormatter('$%.2f'))

        unique_timestamps = df['timestamps'].unique()
        tick_indices = [i for i, x in enumerate(df['timestamps']) if x in unique_timestamps]

        num_ticks = 5
        tick_step = max(1, len(tick_indices) // (num_ticks - 1))
        tick_indices = tick_indices[::tick_step]

        ax.set_xticks(df['timestamps'].iloc[tick_indices])
        ax.set_xticklabels(df['timestamps'].iloc[tick_indices], rotation=45)

        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)

        lines1, labels1 = ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

        plt.suptitle(title)
        #plt.show()

        return fig
