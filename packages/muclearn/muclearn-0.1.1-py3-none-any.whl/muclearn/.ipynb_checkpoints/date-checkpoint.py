import datetime
import holidays
import pandas as pd

__seasons = [
    range(80, 172),   # Spring
    range(172, 264),  # Summer
    range(264, 355)   # Fall
]
__de_by_holidays = holidays.country_holidays("DE", subdiv="BY")

def calculate_datetime_features(df, column="datetime", start_year=None):
    """
    Calculates features which can be derived from standard datetime on a dataframe and return it.
    
    Keyword arguments:
    column -- the datetime column in the passed dataframe
    """
    datetime_column = df[column]
    if start_year is None:
        start_year = datetime_column.dt.year.min()
    df = df.assign(
        hour = datetime_column.dt.hour,
        weekyday = datetime_column.dt.weekday,
        month = datetime_column.dt.month,
        season = datetime_column.dt.dayofyear.apply(__calculate_season),
        year = datetime_column.dt.year - start_year,
        pre_holiday = datetime_column.dt.date.apply(__calculate_holiday, offset=-1),
        holiday = datetime_column.dt.date.apply(__calculate_holiday),
        post_holiday = datetime_column.dt.date.apply(__calculate_holiday, offset=1)
    )
    return df


def __calculate_season(dayofyear):
    for season, i in zip(__seasons, range(len(__seasons))):
        if dayofyear in season:
            return i
    return 3  # Winter


def __calculate_holiday(date, offset=0):
    return int(date - datetime.timedelta(days=offset) in __de_by_holidays)
        