from scipy.stats import norm
import numpy as np

class Segment:

    def __init__(self, name, stocks_df):
        self.name = name
        stocks_df['models'] = stocks_df.apply(
            lambda x: Stock(
                stock_id=x['id'],
                name=x['name'],
                initial_price=x['initial_price'],
                initial_market_cap=x['initial_market_cap'],
                distribution=norm.rvs,
                volatility=x['volatility'],
                mean=x['mean'],
            ),
            axis=1,
        )
        df = stocks_df[['id', 'models']]
        df.index = df['id']
        df = df.drop('id', axis=1)
        stocks_dict = df.to_dict()['models']
        self.stocks = stocks_dict


class Market:

    def __init__(self, name, start, end, df):
        self.name = name
        self.start = start
        self.end = end
        self.segments = {segment[0]: Segment(segment[0], segment[1]) for segment in df.groupby('segment')}

    def stocks(self):
        result = []
        for segment in self.segments.values():
            for stock in segment.stocks.values():
                result.append(stock)
        return result

    def simulate(self):
        number_days = np.busday_count(self.start, self.end)
        for stock in self.stocks():
            stock.daily_returns = stock.distribution(scale=stock.volatility, loc=stock.mean, size=number_days)


class Stock:

    def __init__(self, stock_id, name, initial_price, initial_market_cap, volatility, mean, distribution=norm.rvs):
        """
        :param stock_id:
        :param name:
        :param initial_price:
        :param initial_market_cap:
        :param volatility:
        :param mean:
        :param distribution: must be a function that takes mean, volatility and size, outputs a price vector
        """
        self.stock_id = stock_id
        self.name = name
        self.initial_price = initial_price
        self.initial_market_cap = initial_market_cap
        self.distribution = distribution
        self.volatility = volatility
        self.mean = mean
