import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import bottleneck as bn
import multiprocessing as mp
from fractions import Fraction
from scipy.ndimage import minimum_filter1d, maximum_filter1d
from typing import Tuple, Dict
from functions.evaluation import evaluation

evaluate = evaluation()

class strategies:
    
    def __init__(self):
        variable = None

    def SMA_cross(self, numpy_array: np.ndarray, transaction_cost: float, strategy: int, shorter_period: int, longer_period: int, interval: str) -> Tuple[pd.DataFrame, Dict]:
        # Change position when fast SMA crosses slow SMA

        timestamps = numpy_array[:, 0]
        prices = numpy_array[:, 1].astype(float)
        variables = numpy_array[:, 2].astype(float)
        shorter_ma = bn.move_mean(variables, window=shorter_period)
        longer_ma = bn.move_mean(variables, window=longer_period)
        timestamps = timestamps[longer_period - 1:]
        prices = prices[longer_period - 1:]
        variables = variables[longer_period - 1:]
        shorter_ma = shorter_ma[longer_period - 1:]
        longer_ma = longer_ma[longer_period - 1:]

        positions = np.where(shorter_ma > longer_ma, strategy, -strategy)

        prev_positions = np.zeros_like(prices)
        prev_positions[1:] = positions[:-1]

        pct_changes = np.concatenate((np.array([0]), np.diff(prices) / prices[:-1]))
        price_changes = np.concatenate((np.array([0]), np.diff(prices)))

        trades = positions - np.concatenate((np.array([0]), positions[:-1]))
        costs = np.abs(trades) * transaction_cost

        earnings = prev_positions * price_changes - costs * prices
        pnl = prev_positions * pct_changes - costs
        cum_pnl = np.cumsum(pnl)
        drawdowns = cum_pnl - np.maximum.accumulate(cum_pnl)
        underlying_cumu = np.cumsum(pct_changes)
        underlying_dd = underlying_cumu - np.maximum.accumulate(underlying_cumu)

        short = np.sum(trades < 0)
        long = np.sum(trades > 0)
        n_trade = long + short
        long_short_duration_ratio = np.sum(positions > 0) / np.sum(positions < 0)

        mapping = {
            "1m": 24 * 60,
            "5m": 24 * 12,
            "15m": 24 * 4,
            "30m": 24 * 2,
            "1h": 24
        }
        count = mapping.get(interval, 1)

        # Calculate the number of complete blocks
        num_complete_blocks = len(pnl) // count

        sums_of_complete_blocks = np.sum(pnl[:num_complete_blocks * count].reshape(-1, count), axis=1)
        remaining_sum = np.sum(pnl[num_complete_blocks * count:]) if num_complete_blocks * count < len(pnl) else []
        strategy_daily_pnl = np.concatenate([sums_of_complete_blocks, remaining_sum])

        sums_of_complete_blocks = np.sum(pct_changes[:num_complete_blocks * count].reshape(-1, count), axis=1)
        remaining_sum = np.sum(pct_changes[num_complete_blocks * count:]) if num_complete_blocks * count < len(pct_changes) else []
        asset_daily_pct_change = np.concatenate([sums_of_complete_blocks, remaining_sum])

        sharpe_ratio = evaluate.compute_sharpe_ratio(strategy_daily_pnl)
        calmar_ratio = evaluate.compute_calmar_ratio(strategy_daily_pnl)
        beta = evaluate.compute_beta(strategy_daily_pnl, asset_daily_pct_change)
        maximum_drawdown = evaluate.compute_maximum_drawdown(pnl)

        df = pd.DataFrame({
            'timestamp': timestamps,
            'prices': prices,
            'variables': variables,
            'shorter_ma': shorter_ma,
            'longer_ma': longer_ma,
            'positions': positions,
            'pct_changes': pct_changes,
            'price_changes': price_changes,
            'trades': trades,
            'costs': costs,
            'earnings': earnings,
            'pnl': pnl,
            'cum_pnl': cum_pnl,
            'drawdowns': drawdowns,
            'underlying_cumu': underlying_cumu,
            'underlying_dd': underlying_dd
            })

        result = {
            "shorter_period": shorter_period,
            "longer_period": longer_period,        
            "sharpe_ratio": sharpe_ratio,
            "calmar_ratio": calmar_ratio,
            "maximum_drawdown": maximum_drawdown,
            "long_short_duration_ratio": long_short_duration_ratio,
            "number_of_trades": n_trade
            }

        return df, result

    def bband(self, numpy_array: np.ndarray, transaction_cost: float, strategy: int, z_thresh: float, rolling_period: int, interval: str) -> Tuple[pd.DataFrame, Dict]:
        # Let x be the moving average of a variable, z_th be the z-score threshold, std be the standard deviation.
        # Construct upper band (x + z_th  * std), middle band (x), and lower band (x - z_th * std).
        # Enter when the variable crosses upper band or lower band. Exit when the variable crosses middle band.
        timestamps = numpy_array[:, 0]
        prices = numpy_array[:, 1].astype(float)
        variables = numpy_array[:, 2].astype(float)

        mapping = {
            "1m": 24 * 60,
            "5m": 24 * 12,
            "15m": 24 * 4,
            "30m": 24 * 2,
            "1h": 24
        }
        count = mapping.get(interval, 1)

        period = int(rolling_period)
        sma = bn.move_mean(variables, window=period)
        std = np.sqrt(bn.move_var(variables, window=period))

        timestamps = timestamps[period - 1:]
        sma = sma[period - 1:]
        std = std[period - 1:]
        prices = prices[period - 1:]
        variables = variables[period - 1:]

        z_scores = (variables - sma) / std

        upper_band = sma + z_thresh * std
        lower_band = sma - z_thresh * std

        position = 0
        positions = np.zeros_like(z_scores)
        
        for y, z in enumerate(z_scores):
            if z >= z_thresh:
                positions[y] = strategy
                position = strategy
            elif z <= -z_thresh:
                positions[y] = -strategy
                position = -strategy
            elif z > 0 and position == strategy:
                positions[y] = position
            elif z < 0 and position == -strategy:
                positions[y] = position
            else:
                positions[y] = 0
                position = 0
        
        prev_positions = np.zeros_like(prices)
        prev_positions[1:] = positions[:-1]

        pct_changes = np.concatenate((np.array([0]), np.diff(prices) / prices[:-1]))
        price_changes = np.concatenate((np.array([0]), np.diff(prices)))

        trades = positions - np.concatenate((np.array([0]), positions[:-1]))
        costs = np.abs(trades) * transaction_cost

        earnings = prev_positions * price_changes - costs * prices
        pnl = prev_positions * pct_changes - costs
        cum_pnl = np.cumsum(pnl)
        drawdowns = cum_pnl - np.maximum.accumulate(cum_pnl)
        underlying_cumu = np.cumsum(pct_changes)
        underlying_dd = underlying_cumu - np.maximum.accumulate(underlying_cumu)

        short = np.sum(trades < 0)
        long = np.sum(trades > 0)
        n_trade = long + short
        long_short_duration_ratio = np.sum(positions > 0) / np.sum(positions < 0)

        mapping = {
            "1m": 24 * 60,
            "5m": 24 * 12,
            "15m": 24 * 4,
            "30m": 24 * 2,
            "1h": 24
        }
        count = mapping.get(interval, 1)

        # Calculate the number of complete blocks
        num_complete_blocks = len(pnl) // count

        strategy_daily_pnl = pnl[:num_complete_blocks * count].reshape(-1, count).sum(axis=1)
        sums_of_complete_blocks = np.sum(pnl[:num_complete_blocks * count].reshape(-1, count), axis=1)
        remaining_items = pnl[num_complete_blocks * count:]
        sums_of_remaining = remaining_items.sum() if remaining_items.size > 0 else np.array([])
        strategy_daily_pnl = np.concatenate((strategy_daily_pnl, [sums_of_remaining]))

        asset_daily_pct_change = pct_changes[:num_complete_blocks * count].reshape(-1, count).sum(axis=1)
        sums_of_complete_blocks = np.sum(pct_changes[:num_complete_blocks * count].reshape(-1, count), axis=1)
        remaining_items = pct_changes[num_complete_blocks * count:]
        sums_of_remaining = remaining_items.sum() if remaining_items.size > 0 else np.array([])
        asset_daily_pct_change = np.concatenate((asset_daily_pct_change, [sums_of_remaining]))

        sharpe_ratio = evaluate.compute_sharpe_ratio(strategy_daily_pnl)
        beta = evaluate.compute_beta(strategy_daily_pnl, asset_daily_pct_change)
        maximum_drawdown = evaluate.compute_maximum_drawdown(pnl)
        calmar_ratio = evaluate.compute_calmar_ratio(strategy_daily_pnl, maximum_drawdown)

        df = pd.DataFrame({
            'timestamps': timestamps,
            'prices': prices,
            'variables': variables,
            'sma': sma,
            'upper_band': upper_band,
            'lower_band': lower_band,
            'positions': positions,
            'pct_changes': pct_changes,
            'price_changes': price_changes,
            'trades': trades,
            'costs': costs,
            'earnings': earnings,
            'pnl': pnl,
            'cum_pnl': cum_pnl,
            'drawdowns': drawdowns,
            'underlying_cumu': underlying_cumu,
            'underlying_dd': underlying_dd
            })

        result = {
            'rolling_period': rolling_period,
            'z_thresh': z_thresh,     
            "sharpe_ratio": sharpe_ratio,
            "calmar_ratio": calmar_ratio,
            "maximum_drawdown": maximum_drawdown,
            "long_short_duration_ratio": long_short_duration_ratio,
            "number_of_trades": n_trade
            }

        return df, result
