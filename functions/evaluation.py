import numpy as np

class evaluation:
    
    def __init__(self):
        self.day_count = 365 #cryptocurrency market is 24/7

    def compute_sharpe_ratio(self, strategy_daily_pnl: np.ndarray) -> float:
        # Sharpe Ratio = (mean of daily return % / standard deviation of daily return %) * sqrt(365)
        SR = (self.day_count ** 0.5) * np.mean(strategy_daily_pnl) / np.std(strategy_daily_pnl)  
        return SR
    
    def compute_calmar_ratio(self, strategy_daily_pnl: np.ndarray, maximum_drawdown: float) -> float:
        # Calmar_ratio = average annual return / |maximum_drawdown|
        cumulative_return = (1 + strategy_daily_pnl).prod()
        avg_annual_return = (cumulative_return ** (1 / (len(strategy_daily_pnl) / self.day_count) )) - 1
        CR = avg_annual_return / -maximum_drawdown
        return CR
    
    def compute_beta(self, strategy_daily_pnl, asset_daily_pct_change: np.ndarray):
        # beta = covariance(strategy daily return, buy and hold daily return) / variance(buy and hold daily return)
        np.cov(asset_daily_pct_change, strategy_daily_pnl)[0, 1] / np.var(asset_daily_pct_change)

    def compute_maximum_drawdown(self, pnl: np.ndarray) -> float:
        # maximum of absolute value of drawdowns
        cumulative_earnings_pct = np.cumsum(pnl)
        drawdowns = cumulative_earnings_pct - np.maximum.accumulate(cumulative_earnings_pct)
        MDD = np.min(drawdowns)
        return MDD
