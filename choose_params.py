# Choose_params.py
# Purpose: Check the performance of a trading strategy with specific chosen parameters.
# After execution, equity curve and bband graph can be found in /heatmaps and /bband_graphs folders respectively.

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

z_thresh = 1.8
rolling_period = 1680
test_no = 0

na = np.genfromtxt(f"cleaned_data/{pair}_{data_name}_price_{interval}.csv", delimiter=',', skip_header=1, dtype=str)
test_set_0 = na[:, [0,1,2]]
data_count = test_set_0.shape[0]
test_sets = [test_set_0, test_set_0[ : int(data_count/3), :], test_set_0[int(data_count/3):int(2*data_count/3), :], test_set_0[int(2*data_count/3):, :]]
test_set = test_sets[test_no]

# Perform BBand
result = st.bband(test_set, transaction_cost, strategy, z_thresh, rolling_period, interval)
result_df = result[0] # pd.DataFrame for debugging
performance = result[1] # evaluation

result_df.to_csv("csv_debug/result.csv")

# Show the performance
print("***************************************************************************************")
print("coin: " + coin)
print(f"strategy name: {strategy_name} on {data_name}")
print(f"z-score threshold: {str(round(z_thresh, 2))}")
print(f"rolling_period: {str(round(rolling_period, 2))}")
print(f"sharpe ratio: {str(round(performance["sharpe_ratio"], 2))}")
print(f"calmar ratio: {str(round(performance["calmar_ratio"], 2))}")
print(f"maximum drawdown: {str(round(performance["maximum_drawdown"] * 100, 2))}%")
print(f"number_of_trades: {str(round(performance["number_of_trades"], 2))}")
print(f"long_short_duration_ratio: {str(round(performance["long_short_duration_ratio"], 2))}")
print(f"acc_return: {str(round(result_df["cum_pnl"][len(result_df)-1] * 100, 2))}%")
print("***************************************************************************************")


title = f"{pair} {data_name} {strategy_name} ({interval} data) (z_thresh = {z_thresh}, rolling_period = {rolling_period})"

# Generate Equity Curve
ylabel = "Cumulative PNL"
xlabel = "Time"
fig = vi.generate_equity_curve(result_df, title, ylabel, xlabel)
folder_path = "equity_curves"
file_name = f"test_{test_no}.png"
save_path = os.path.join(folder_path, file_name)
fig.savefig(save_path, dpi=300)

print(f"test {test_no} is finished")
print(f"Equity Curve can be found in /{folder_path}")

# Generate Bband Graph
ylabel = data_name
xlabel = "Time"
fig = vi.bband_visualization(result_df, title, ylabel, xlabel)
folder_path = "bband_graphs"
file_name = f"test_{test_no}.png"
save_path = os.path.join(folder_path, file_name)
fig.savefig(save_path, dpi=300)

print(f"test {test_no} is finished")
print(f"Bband graph can be found in /{folder_path}")

