import pandas as pd
from models.models import Market


def load_data(name, start, end, path):
    try:
        data = pd.read_csv(path)
    except IOError as err:
        print(err)
        data = pd.read_excel(path)
    return market_builder(name, start, end, data)


def market_builder(name, start, end, df):
    return Market(name, start, end, df)