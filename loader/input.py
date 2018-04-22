import pandas as pd
from models.models import Market

import datetime

def load_data(name, start, end, path):
    try:
        data = pd.read_csv(path)
    except IOError as err:
        print(err)
        data = pd.read_excel(path)
    return market_builder(name, start, end, data)


def market_builder(name, start, end, df):
    return Market(name, start, end, df)

if __name__ == "__main__":

    # create market object
    market = load_data('Test',datetime.date(2018,1,1), datetime.date(2019,1,1), r'C:\Users\Erik\ardaProject\arda\stocks.csv')

    report = market.simulate(0.5,0.5)
