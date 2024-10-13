import warnings
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from backtesting.test import SMA, GOOG
import pandas as pd

warnings.simplefilter(action='ignore', category=FutureWarning)


def rsi(data, period=14):
    series = pd.Series(data)
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))


GOOG.index = pd.to_datetime(GOOG.index)
dataFiltered = GOOG.loc['2012-01-01':'2018-01-01']


class MySmaStrategy(Strategy):
    def init(self):
        price = self.data.Close

        #10 day moving average
        self.ma1 = pd.Series(self.I(SMA, price, 10)).dropna().values

        #20 day moving average
        self.ma2 = self.I(SMA, price, 20)

        #RSI values calculated for the last 14 trading days at any point, has 237 values since 365 - 52(2) (weekends) - 13 (the first 13 days wont have a previous 14 day RSI)
        self.rsiValues = pd.Series(self.I(rsi, price, 14)).dropna().values

        



    def next(self):
        if crossover(self.ma1, self.ma2):
            self.buy()
        elif crossover(self.ma2, self.ma1):
            self.sell()


backtest = Backtest(dataFiltered, MySmaStrategy, commission=.002, exclusive_orders=True)
stats = backtest.run()
print(stats)