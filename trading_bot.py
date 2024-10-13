import warnings
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from backtesting.test import SMA, GOOG
import pandas as pd
import requests
from textblob import TextBlob

warnings.simplefilter(action='ignore', category=FutureWarning)

# Function to calculate RSI
def rsi(data, period=14):
    series = pd.Series(data)
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# Function to fetch news using NewsAPI
def fetch_news(symbol, api_key):
    url = f'https://newsapi.org/v2/everything?q={symbol}&sortBy=publishedAt&apiKey={api_key}'
    response = requests.get(url)
    news_data = response.json()
    
    articles = [article['title'] for article in news_data['articles']]
    return articles

# Function to perform sentiment analysis on news articles
def sentiment_analysis(text):
    blob = TextBlob(text)
    sentiment = blob.sentiment.polarity
    return sentiment

# Load and filter Google stock data
GOOG.index = pd.to_datetime(GOOG.index)
dataFiltered = GOOG.loc['2012-01-01':'2018-01-01']

# Trading strategy class
class MySmaStrategy(Strategy):
    api_key = 'YOUR_NEWSAPI_KEY'  # Replace with your actual NewsAPI key
    symbol = 'GOOG'  # Symbol for the stock you're trading

    def init(self):
        price = self.data.Close

        # 10 day moving average
        self.ma1 = pd.Series(self.I(SMA, price, 10)).dropna().values

        # 20 day moving average
        self.ma2 = self.I(SMA, price, 20)

        # RSI values calculated for the last 14 trading days
        self.rsiValues = pd.Series(self.I(rsi, price, 14)).dropna().values

        # Fetch the latest news and calculate the sentiment score
        articles = fetch_news(self.symbol, self.api_key)
        if articles:
            self.sentiment_score = sum([sentiment_analysis(article) for article in articles]) / len(articles)
        else:
            self.sentiment_score = 0  # If no articles are found, neutral sentiment

    def next(self):
        # Use sentiment score along with moving average crossovers for buy/sell decisions
        if crossover(self.ma1, self.ma2) and self.sentiment_score > 0:
            self.buy()
        elif crossover(self.ma2, self.ma1) and self.sentiment_score < 0:
            self.sell()

# Run backtest
backtest = Backtest(dataFiltered, MySmaStrategy, commission=.002, exclusive_orders=True)
stats = backtest.run()
print(stats)
