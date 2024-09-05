# Backtesting.py
# Purpose: Back-testing a trading strategy.
# After execution, heatmap can be found in /heatmaps folder.

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import bottleneck as bn
import multiprocessing as mp
from fractions import Fraction
import pandas as pd
import os

from functions.strategy import strategies
from functions.visualization import visualization

st = strategies()
vi = visualization()

# Prepare dataset
coin = "BTC"
pair = f"{coin}USDT"
endpoint = "https://api.glassnode.com/v1/metrics/distribution/balance_exchanges"
data_name = endpoint.split('/')[-1]
interval = "1h"
exchange = "binance"

strategy_name = "bband"
transaction_cost = 0.0006
strategy = -1

z_threshes = np.array([0.0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2, 2.4, 2.6, 2.8, 3.0])
rolling_periods = np.array([24, 48, 96, 144, 192, 240, 360, 480, 600, 720, 840, 960, 1200, 1440, 1680, 1920, 2160, 2400])

na = np.genfromtxt(f"cleaned_data/{pair}_{data_name}_price_{interval}.csv", delimiter=',', skip_header=1, dtype=str)
test_set_0 = na[:, [0,1,2]]
data_count = test_set_0.shape[0]
test_sets = [test_set_0, test_set_0[ : int(data_count/3), :], test_set_0[int(data_count/3):int(2*data_count/3), :], test_set_0[int(2*data_count/3):, :]]

# Test all test sets

for test_no in range(len(test_sets)):
    print(f"test set {test_no}")
    test_set = test_sets[test_no]

    sharpe_table = np.zeros((len(z_threshes), len(rolling_periods)))
    calmar_table = np.zeros((len(z_threshes), len(rolling_periods)))
    n_trade_table = np.zeros((len(z_threshes), len(rolling_periods)))
    long_short_duration_ratio_table = np.zeros((len(z_threshes), len(rolling_periods)))

    for i, z_thresh in enumerate(z_threshes):
        for j, rolling_period in enumerate(rolling_periods):
            # loop every combination of parameters
            result = st.bband(test_set, transaction_cost, strategy, z_thresh, rolling_period, interval)
            result_df = result[0] # pd.DataFrame for debugging
            performance = result[1] # evaluation

            sharpe_table[i, j] = performance["sharpe_ratio"]
            calmar_table[i, j] = performance["calmar_ratio"]
            n_trade_table[i, j] = performance["number_of_trades"]
            long_short_duration_ratio_table[i, j] = performance["long_short_duration_ratio"]

    # Generate Heatmaps
    fig = vi.generate_heatmap(sharpe_table, calmar_table, 
                                  n_trade_table, long_short_duration_ratio_table, 
                                  rolling_periods, z_threshes, 
                                  "rolling_periods", "z_threshes")

    folder_path = "heatmaps"
    file_name = f"test_{test_no}.png"
    save_path = os.path.join(folder_path, file_name)

    #Save the Heatmaps
    fig.savefig(save_path, dpi=300)
    
    print(f"test {test_no} is finished")
    print(f"heatmaps can be found in /{folder_path}")


