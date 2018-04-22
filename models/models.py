import pandas as pd

from functions.stats import rvs
from pandas.tseries.offsets import BDay


class Segment:

    def __init__(self, name, stocks_df):
        self.name = name
        stocks_df['models'] = stocks_df.apply(
            lambda x: Stock(
                stock_id=x['id'],
                name=x['name'],
                initial_price=x['initial_price'],
                initial_market_cap=x['initial_market_cap'],
                distribution=rvs,
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

    def work_days(self):
        return pd.date_range(self.start, self.end, freq=BDay())

    def simulate(self, stock_kwargs, *args, **kwargs):
        result = {}

        for stock in self.stocks():
            kwargs_clone = {**kwargs}
            for key, attribute_name in stock_kwargs.items():
                kwargs_clone[key] = getattr(stock, attribute_name)
            result[stock.stock_id] = stock.distribution(market=self, *args, **kwargs_clone)

        work_days = kwargs.get('work_days')

        return Report(result, work_days)


class Stock:

    def __init__(self, stock_id, name, initial_price, initial_market_cap, volatility, mean, distribution):
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


class Report:

    def __init__(self, data_dict, days):
        self.data = {stock: pd.DataFrame(data=list(zip(days, data_dict[stock])), columns=['date', 'return'])
                     for stock in data_dict}