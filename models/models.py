import pandas as pd


class Segment:

    def __init__(self, name, stocks_df):
        self._name = name
        self._stocks = stocks_df


class Market:

    def __init__(self, name, start, end, df):
        self._name = name
        self._start = start
        self._end = end
        self._segments = {segment[0]: Segment(segment[0], segment[1]) for segment in df.groupby('segment')}


class Stock:

    def __init__(self, id, name, initial, segment):
        pass
