import datetime
import holidays
import json
import pandas as pd

__seasons = [
    range(80, 172),   # Spring
    range(172, 264),  # Summer
    range(264, 355)   # Fall
]
__de_by_holidays = holidays.country_holidays("DE", subdiv="BY")

with open("ferien_by.json", "r") as file:
    __ferien_by = json.load(file, parse_int=True)

def calculate_datetime_features(df, column="datetime", start_year=None):
    """
    Calculates features which can be derived from standard datetime on a dataframe and return it.
    
    Current features are:
    - hour
    - weekday
    - month
    - season
    - year
    - Bavarian holidays (german: "Bayerische Feiertage") including days before (pre_) and after (post_)
    - Bavarian school holidays (german: "Bayerische Schulferien") ()
    
    Keyword arguments:
    column -- the datetime column in the passed dataframe
    """
    datetime_column = df[column]
    if start_year is None:
        start_year = datetime_column.dt.year.min()
    df = df.assign(
        hour = datetime_column.dt.hour,
        weekday = datetime_column.dt.weekday,
        month = datetime_column.dt.month,
        season = datetime_column.dt.dayofyear.apply(__calculate_season),
        year = datetime_column.dt.year - start_year,
        pre_holiday = datetime_column.dt.date.apply(__calculate_holiday, offset=-1),
        holiday = datetime_column.dt.date.apply(__calculate_holiday),
        post_holiday = datetime_column.dt.date.apply(__calculate_holiday, offset=1),
        ferien_by = datetime_column.dt.date.apply(__calculate_ferien),
    )
    return df


def __calculate_season(dayofyear):
    for season, i in zip(__seasons, range(len(__seasons))):
        if dayofyear in season:
            return i
    return 3  # Winter


def __calculate_holiday(date, offset=0):
    return int(date - datetime.timedelta(days=offset) in __de_by_holidays)
        
    
def __calculate_ferien(date):
    year_index = date.year
    if date.month == 1:
        year_index -= 1
    if str(year_index) not in __ferien_by.keys():
        return 0
    for start, end in __ferien_by[str(year_index)].values():
        if date >= datetime.date.fromisoformat(start) and date <= datetime.date.fromisoformat(end):
            return 1
    if date.weekday() == 5:
        before = __calculate_ferien(date + datetime.timedelta(days=2))
        after = __calculate_ferien(date - datetime.timedelta(days=1))
        if before or after:
            print(date)
    if date.weekday() == 6:
        before = __calculate_ferien(date + datetime.timedelta(days=1))
        after = __calculate_ferien(date - datetime.timedelta(days=2))
        if before or after:
            print(date)
    return 0