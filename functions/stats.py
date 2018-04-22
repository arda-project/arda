import pandas as pd
from scipy.stats import norm


def rvs(market, scale, loc, work_days, *args, **kwargs):
    """
    A wrapper of scipy.stats.norm.rvs
    """
    return norm.rvs(scale=scale, loc=loc, size=len(work_days))
