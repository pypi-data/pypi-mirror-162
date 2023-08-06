# -*- coding: utf-8 -*-
import pandas as pd

import sys
sys.path.append('src/algobacktest')
import Backtest as bt



def test_getprice():
    test_data = bt.getprice('AAPL', start='2022-08-01', end='2022-08-02')
    valid_data = pd.DataFrame([['2022-08-01', 161.2859649658203],
                               ['2022-08-02', 159.7880401611328]],
                              columns=['Date', 'Adj Close']). \
        set_index('Date')['Adj Close']
    valid_data.index = pd.to_datetime(valid_data.index)
    dates_equal = (valid_data.index[0] == test_data.index[0]) & \
        (valid_data.index[1] == test_data.index[1])

    prices_equal = (valid_data[0] == test_data[0]) & \
        (valid_data[1] == test_data[1])

    assert dates_equal & prices_equal
