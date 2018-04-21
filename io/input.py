import pandas as pd
from models.models import Market


def load_data(path):
    try:
        return pd.read_csv(path)
    except:
        return pd.read_excel(path)


def market_builder(start, end, df):
    return Market(start, end, df)