# -*- coding: utf-8 -*-
"""Getting data, making strategy and backtesting."""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pandas_datareader.data as pdr


def getprice(symbol, start='2020-01-01', end='2022-06-30'):
    """
    Gets historical stock prices from Yahoo Finance

    Parameters
    ----------
    symbol : str
        Yahoo Finance listed ticker.
    start : str, optional
        Start date for historical data in YYYY-mm-dd format.
        The default is '2020-01-01'.
    end : str, optional
        Start date for historical data in YYYY-mm-dd format.
        The default is '2022-06-30'.

    Returns
    -------
    pandas dataframe
        Index as datetime and Adj Close column as closing price.

    """

    data = pdr.DataReader(symbol, 'yahoo', start=start, end=end)
    return data['Adj Close']


def getsma(prices, window=14):
    """
    Gives daily Simple Moving Average strategy trading positions.

    Parameters
    ----------
    prices : pandas series or dataframe
        daily closing prices.
    window : int, optional
        rolling window for moving average. The default is 14.

    Returns
    -------
    positions : pandas Series
        Daily trading positions:
            0 for no open position,
            1 for long position.

    """
    sma = prices.rolling(window).mean()
    signals = []
    for day_price, day_sma in zip(prices, sma):
        if day_price < day_sma:
            signals.append(0)
        elif day_price >= day_sma:
            signals.append(1)
        else:
            signals.append(np.nan)
    signals = pd.Series(signals)
    positions = signals.shift(1)
    return positions


class Test:
    """
    Test significance of backtesting result using monte carlo simulation.
    """

    def __init__(self):
        self.prices = []
        self.positions = []

    def detrend_returns(self):  # log returns
        """
        Detrend returns to eliminate position bias.
        """
        logrets = np.log(self.prices / self.prices.shift(1)).rename('return')
        avg_return = logrets.mean()
        self.detrended_logret = logrets - avg_return

    def run_montecarlo(self, run=1000, seed=101):
        """
        Monte Carlo permutation of detrended stock returns.

        Parameters
        ----------
        run : int, optional
            Number of monte carlo series created. The default is 1000.
        seed : int, optional
            Numpy random seed. The default is 101.

        Returns
        -------
        None.

        """
        num_days = len(self.detrended_logret)
        mu = self.detrended_logret.mean()
        sigma = self.detrended_logret.std()
        np.random.seed(seed)
        all_simulations = []
        for _ in range(run):
            simulated_returns = np.random.normal(
                loc=mu, scale=sigma, size=num_days)
            all_simulations.append(simulated_returns)
        self.all_simulations = pd.DataFrame(all_simulations)

    def calculate_trade_results(self):
        """
        Calculate Monte carlo series trade returns.

        Returns
        -------
        None.

        """
        self.sim_ret = (self.all_simulations @ self.positions.dropna().values) / \
            len(self.positions.dropna()) * 252

    def run(self):
        """
        Execute backtest.

        Returns
        -------
        None.

        """
        self.prices
        self.positions
        self.detrend_returns()
        self.detrended_logret = self.detrended_logret[-len(self.positions.dropna()):]
        self.strategy_return = np.mean(
            self.detrended_logret.values * self.positions.dropna().values)*252
        self.run_montecarlo()
        self.calculate_trade_results()

    def plot_significance(self):
        """
        Visualize significance test.

        Returns
        -------
        None.

        """
        self.sim_ret.plot(kind='hist', bins=50)
        plt.axvline(self.strategy_return, c='r')
        plt.title('Backtest Significange')
        plt.xlabel('Strategy Avg Annual Returns')
        plt.ylabel('Frequency')
        plt.show()
