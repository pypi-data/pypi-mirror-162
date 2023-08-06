# Author: Salyl Bhagwat, Gammath Works
# Copyright (c) 2021-2022, Salyl Bhagwat, Gammath Works
# All Rights Reserved
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

__author__ = 'Salyl Bhagwat'
__copyright__ = 'Copyright (c) 2021-2022, Salyl Bhagwat, Gammath Works'

import pandas as pd
import yfinance as yf
import sys


def main():

    ticker = yf.Ticker('AAPL')

    try:
        # Get 10Y stock history using 10Y-period
        stock_history = ticker.history('1mo', interval='5m')
    except:
        raise RuntimeError('Error obtaining stock history')

    stock_history_len = len(stock_history)

    if (stock_history_len > 0):

        try:

            #Entries with nan values cause problems during analysis so drop those
            #Save the new history after dropping rows with nan values
            stock_history.dropna(how='any').to_csv(f'AAPL_long_history.csv')

        except:
            raise RuntimeError('Stock history file RW error')
    else:
        raise ValueError('Invalid length stock history')

    return
    
if __name__ == '__main__':
    main()
