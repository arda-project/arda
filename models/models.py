import pandas as pd

from pandas.tseries.offsets import BDay
from scipy.stats import norm
import numpy as np
from scipy import stats

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

    def simulate(self,marketVolaPart, sectorVolaPart):
        result = {}
        days = pd.date_range(self.start, self.end, freq=BDay())
        number_days = len(days)

        # # # erik code
        # build volatility dict
        volaDict = {'internet': [0.1,0.1], 'semiconductor':[0.1,0.1], 'crazytech': [0.1,0.1]}

        # build drift dict
        driftList = [[x.stock_id, x.mean] for x in self.stocks()]
        driftDict = {k[0]: k[1] for k in driftList}

        # build a list with all segments
        segementsList = list(self.segments.keys())

        # build a dict which has for every stock its segment as key
        stockSegments = {}
        for seg in segementsList:
            arr = [stock for stock in self.segments[seg].stocks]
            for stock in arr:
                stockSegments[stock] = seg

        corrSegments = [[1, 0.8, 0.8], [0.8, 1, 0.8], [0.8, 0.8, 1]]
        corrStocks = {'internet': [[1, 0.9], [0.9, 1]], 'semiconductor': [[1, 0.9], [0.9, 1]],
                      'crazytech': [[1, 0.9], [0.9, 1]]}

        # # # erik code
        for stock in self.stocks():
            #result[stock.stock_id] = stock.distribution(scale=stock.volatility, loc=stock.mean, size=number_days)
            result = self.myfunc(volaDict, driftDict, corrStocks, corrSegments, stockSegments,
                            marketVolaPart, sectorVolaPart,number_days)
        return Report(result, days)

    def myfunc(self, vola, drift, corrStocks, corrSegments, stockSegment, marketVolaPart, sectorVolaPart,length):

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # deannulize volatility
        for key, value in vola.items():
            vola[key] = value / np.sqrt(255)

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # generate market return
        vola_market = np.concatenate(list(vola.values()))
        vola_market_min = np.min(vola_market) * marketVolaPart

        market_return = np.random.normal(0, vola_market_min, size=length)

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # loop over segments and calculate returns
        segReturns_part1 = stats.multivariate_normal.rvs(
            np.zeros(len(vola.keys())), np.eye(len(vola.keys())), size=length)

        segReturns_part2 = stats.multivariate_normal.rvs(
            np.zeros(len(vola.keys())), np.eye(len(vola.keys())), size=length)

        volaSegs = {}
        for seg in vola.keys():
            volaSegs[seg] = \
                np.min(vola[seg] - vola_market_min) * sectorVolaPart

        # # #

        Cov1 = np.dot(np.dot(np.diag(list(volaSegs.values())), corrSegments),
                      np.diag(list(volaSegs.values())))
        A1 = np.linalg.cholesky(Cov1)

        volaVec = np.sqrt(2 * np.array(list(volaSegs.values())) * vola_market_min)
        Cov2 = np.dot(np.dot(np.diag(volaVec), corrSegments),
                      np.diag(volaVec))
        A2 = np.linalg.cholesky(Cov2)

        for i in range(0, len(segReturns_part1)):
            segReturns_part1[i, :] = np.dot(A1, segReturns_part1[i, :])
            segReturns_part2[i, :] = np.dot(A2, segReturns_part2[i, :])

        # # # loop over segemnt keys and index or sth
        segReturns = {}
        for index, key in enumerate(vola):
            segReturns[key] = segReturns_part1[:, index] + segReturns_part2[:, index]

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # calculate returns for stock level
        volaStocks = {}
        for seg in vola.keys():
            volaStocks[seg] = vola[seg] - vola_market_min - volaSegs[seg]

        stockReturns = {}
        for seg in corrStocks.keys():

            stockReturns_part1 = stats.multivariate_normal.rvs(
                np.zeros(len(corrStocks[seg])), np.eye(len(volaStocks[seg])),
                size=length)

            stockReturns_part2 = stats.multivariate_normal.rvs(
                np.zeros(len(corrStocks[seg])), np.eye(len(volaStocks[seg])),
                size=length)

            stockReturns_part3 = stats.multivariate_normal.rvs(
                np.zeros(len(corrStocks[seg])), np.eye(len(volaStocks[seg])),
                size=length)

            Cov1 = np.dot(np.dot(np.diag(volaStocks[seg]), corrStocks[seg]),
                          np.diag(volaStocks[seg]))
            volaVec2 = np.sqrt(2 * volaStocks[seg] * vola_market_min)
            Cov2 = np.dot(np.dot(np.diag(volaVec2), corrStocks[seg]),
                          np.diag(volaVec2))
            A1 = np.linalg.cholesky(Cov1)

            A2 = np.linalg.cholesky(Cov2)

            volaVec3 = np.sqrt(2 * volaStocks[seg] * volaSegs[seg])
            Cov3 = np.dot(np.dot(np.diag(volaVec3), corrStocks[seg]),
                          np.diag(volaVec3))
            A3 = np.linalg.cholesky(Cov3)

            for i in range(0, len(segReturns_part1)):
                stockReturns_part1[i, :] = np.dot(A1, stockReturns_part1[i, :])
                stockReturns_part2[i, :] = np.dot(A2, stockReturns_part2[i, :])
                stockReturns_part3[i, :] = np.dot(A3, stockReturns_part3[i, :])

            for i, y in enumerate([x for x in stockSegment if stockSegment[x] == seg]):
                stockReturns[y] = stockReturns_part1[:, i] + \
                                  stockReturns_part2[:, i] + stockReturns_part3[:, i] + drift[y] / 255

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # create result dict
        result = {}

        for stock in stockSegment:
            result[stock] = market_return + segReturns[stockSegment[stock]] \
                            + stockReturns[stock]

        return result

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


class Report:

    def __init__(self, data_dict, days):
        self.data = {stock: pd.DataFrame(data=list(zip(days, data_dict[stock])), columns=['date', 'return'])
                     for stock in data_dict}