# Cryptocurrency Trading Strategy Backtesting Framework

## Overview
This is a simple backtesting engine for cryptocurrency trading strategies. It allows users to simulate trades and evaluate the performance of different strategies using historical data.

## Purpose
Internal Training / Tutorial about Trading Strategy Backtesting
Let readers understand the basic framework of backtesting as fast as possible

## Quick Start
1. Git clone this repository to your local computer. 
2. Run data_preparation.py to fetch and save data.
3. Run backtesting.py to generate heatmaps.
4. Based on the heatmaps, choose the best parameters. Type the chosen parameters in choose_params.py and run it.
    Strategy evaluation, equity curves, and bband demonstration can be found.
4. Feel free to adjust the code for backtesting!

## Framework

### Data Preparation

1. **Choose Data**
    Useful APIs: Exchanges (e.g., Binance, Bybit, Coinbase) Glassnode, Coinalyze, Coinglass, Cryptoquant, Santiment, Nodechart
    Please carefully check the definition of a data before backtesting

2. **Fetch Data**
    In data_preparation.py, price and exchange balance are fetched from several APIs.
    You can adjust the params like startDate, endDate, interval, etc.
    For deeper understanding, chect /functions/fetch_data.py
    Please be reminded that you should always check the API documentation if you want to fetch new data.

3. **Clean Data**
    People always underestimate the importance of data cleaning. Here are some potential issues:
    Missing data, Duplicated rows, merging datasets, inconsistent attribute name, timestamp
    Also, you need to adjust the format of dataframe to fit the requirement of backtesting engine
    In data_preparation.py, price_df and exchange_balance_df are merged.

4. **Test Set**
    To avoid overfitting, we need to separate the dataset into train sets and test set. Select the best model and best parameters that fit train set and then apply them on test sets. There are many ways to separate the dataset. Our common practice is to separate by market (Bull market and Bear Market)

### Build Model

1. **Introduction**
    For beginners, the simplest way of thinking trading strategy is to observe the causation between the price and some variables. The two models below focus on whether current value of a factor is at its historical high (or low) level.
    Bollinger Band is more effective when the variable's trend is more stable and smooth.
    Detailed implementation of these models can be found in /functions/strategy.py

2. **Simple Moving Average Crossover**
    The moving average crossover relies on two moving averages, one longer and one shorter, crossing over each other. We need to decide whether to buy or sell when "golden cross" occurs.
    
    A “golden cross” occurs when the fast moving average crosses up through the slow moving average. This cross occurs because the short-term average moves upward “faster” than the long-term average. 
    A “death cross” occurs when the fast moving average crosses down through the slow moving average. This cross occurs because the short-term average is falling quicker than the long-term average. 
    
    Parameters: fast moving average rolling period & slow moving average rolling period

3. **Bollinger Band**
    Bollinger Bands consist of three bands total: an upper band, middle band, and lower band.
    
    Let x be the moving average of a variable, z_th be the z-score threshold, std be the standard deviation.
    upper band: x + z_th  * std
    middle band: x
    lower band x - z_th * std
    
    Enter the market when the variable crosses upper band or lower band. 
    Exit the market when the variable crosses middle band.

    Parameters: z-score threshold and moving average roling period

    In this engine, bband on exchange balance will be demonstrated.

### Evaluation

1. **Sharpe Ratio**
    Sharpe Ratio is a measure of risk-adjusted return.
    Sharpe Ratio = (mean of daily return % / standard deviation of daily return %) * sqrt(365)
2. **Calmar Ratio**
    Calmar ratio is a measure of risk-adjusted returns.
    Calmar_ratio = average compounded annual rate of return / -maximum_drawdown
3. **Beta**
    Beta denotes the volatility or systematic risk of a security or portfolio compared to the market.
    beta = covariance(strategy daily return, buy and hold daily return) / variance(buy and hold daily return)
4. **Long Short Duration Ratio**
    Long Short Duration Ratio aims to avoid bias to either long or short position.
    Long Short Duration Ratio refers to the ratio between long-buy duration and short-sell duration throughout the dataset length.
5. **Equity Curves**
    We will plot both cumulative PnL of implementing the strategy and cumulative PnL of buy-and-holding an asset. The purpose is similar to computing strategy beta: check the systematic risk of the strategy.
    Moreover, we also want to check whether the equity curve is smooth or not.

### Select Parameters

1. **Generate Sharpe Ratio Heatmap**
    In backtesting.py, you will find that We loop every combination of parameters and run the model again and again. After that, a sharpe ratio table is created and further visualized by a heatmap.
    The ideal scenario is that a significantly large area of the heatmap is blue (which implies high Sharpe Ratio.) Then we are confident to conclude that at least our direction is correct.

2. **Check Details!**
    Apart from the historical profitability of a strategy, we also need to ask:
    "Does it only work in either bull market or bear market?"
    "Is the trading frequency high enough?"
    "Does the strategy perform better than just long-buying? Check equity curves."
    "Do most of the test sets give similar result?"

3. **Improvement**
    After confirming the effectiveness of the trading strategy, we must want to improve it.
    Unsurprising, this step is the most challenging and time-consuming step. You may want to get data with higher resolution. You may want to combine different data sets to get some insights. 
    At the moment, you are like a scientist testing every posible way to improve your strategy.

4. **Apply the model to the test set**
    In the previous steps, you only apply your model to the train sets. Finally, the real effectiveness of the model will be proven by applying the model to the test set. In the process, you can use statistical tools like p-test to ensure that the strategy is profitable in the test set.

### Conclusion
    In conclusion, the framework for trading strategies backtesting serves as a critical tool for evaluating the effectiveness and robustness of various trading approaches. By simulating historical market conditions, it allows traders to assess potential performance metrics, such as returns and risk exposure, while minimizing the uncertainties associated with real-time trading. This systematic analysis not only enhances decision-making but also fosters a deeper understanding of market dynamics and strategy optimization. 

