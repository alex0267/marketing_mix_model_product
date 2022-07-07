" All seasonality & events related features """
import datetime as dt
from datetime import timedelta
from functools import partial
from typing import List, Tuple, Union

import numpy as np
import pandas as pd
from dateutil.easter import easter

#from matrix.st_response_model.model_settings import model_settings
import datetime_module


def _is_easter_year_week(year_week: pd.Series) -> pd.Series:
    week_easter = pd.to_datetime(year_week.floordiv(100).apply(easter))
    week_easter = week_easter.apply(datetime_module.to_isocalendar_year_week)
    return (year_week == week_easter).astype(int)


def _is_saint_patrick(year_week: pd.Series) -> pd.Series:
    """PRUK specific event"""
    saint_patrick_days = pd.Series(
        [dt.datetime(year, 3, 17) for year in set(year_week.apply(datetime_module.get_calendar_year_from_year_index))]
    )

    year_weeks_saint_patrick = saint_patrick_days.apply(datetime_module.to_isocalendar_year_week)
    return year_week.isin(year_weeks_saint_patrick).astype(int)


def _is_pay_day_events(year_week: pd.Series) -> pd.Series:
    """PRJ specific event"""
    contains_25th = partial(datetime_module.contains_month_day_in_year_week, day=25)
    return year_week.apply(contains_25th).astype(int)


def _is_first_week_of_the_month(year_week: pd.Series) -> pd.Series:
    """PR SPAIN specific event"""
    is_first_week = partial(datetime_module.contains_month_day_in_year_week, day=1)
    return year_week.apply(is_first_week).astype(int)


def _is_golden_week_holidays(year_week: pd.Series) -> pd.Series:
    """PRJ specific holidays"""
    days_golden_weeks = pd.Series(
        [
            dt.datetime(year, 4, 30) + timedelta(days=k)
            for year in set(year_week.apply(datetime_module.get_calendar_year_from_year_index))
            for k in range(8)
        ]
    )
    year_weeks_golden_week = days_golden_weeks.apply(datetime_module.to_isocalendar_year_week)
    return year_week.isin(year_weeks_golden_week).astype(int)


def _is_halloween(year_week: pd.Series) -> pd.Series:
    return _is_specific_date(year_week, 10, 31)


def _is_christmas(year_week: pd.Series) -> pd.Series:
    return _is_specific_date(year_week, 12, 25)


def _is_4th_july(year_week: pd.Series) -> pd.Series:
    return _is_specific_date(year_week, 7, 4)


def _is_cinco_mayo(year_week: pd.Series) -> pd.Series:
    return _is_specific_date(year_week, 5, 5)


def _is_father_day(year_week: pd.Series) -> pd.Series:
    return _is_specific_date(year_week, 6, 20)


# TODO: only one st_patrick function
def _is_st_patrick_off_grocery(year_week: pd.Series) -> pd.Series:
    st_patrick = (
        _is_specific_date(year_week, 3, 17, 2018)
        | _is_specific_date(year_week, 3, 24, 2018)
        | _is_specific_date(year_week, 3, 17, 2019)
        | _is_specific_date(year_week, 3, 17, 2020)
    )
    return st_patrick


def _is_st_patrick_off_liquor(year_week: pd.Series) -> pd.Series:
    st_patrick = (
        _is_specific_date(year_week, 3, 17, 2018)
        | _is_specific_date(year_week, 3, 16, 2019)
        | _is_specific_date(year_week, 3, 17, 2020)
    )
    return st_patrick


def _is_st_patrick_off_nabca(year_week: pd.Series) -> pd.Series:
    st_patrick = (
        _is_specific_date(year_week, 3, 17, 2018)
        | _is_specific_date(year_week, 3, 16, 2019)
        | _is_specific_date(year_week, 3, 17, 2020)
    )
    return st_patrick


def _is_second_week(year_week: pd.Series) -> pd.Series:
    _, week = datetime_module.parse_year_index(year_index=year_week)
    second_week = (week == 2).astype(int)
    return second_week


def _is_first_week2019_off_nabca(year_week: pd.Series) -> pd.Series:
    year, week = datetime_module.parse_year_index(year_index=year_week)
    first_week2019 = ((week == 1) & (year == 2019)).astype(int)
    return first_week2019


def _is_week52_2020_off_nabca(year_week: pd.Series) -> pd.Series:
    year, week = datetime_module.parse_year_index(year_index=year_week)
    week52_2020 = ((week == 52) & (year == 2020)).astype(int)
    return week52_2020


def _thanksgiving(year_week: pd.Series) -> pd.Series:
    thanksgiving = (
        _is_specific_date(year_week, 11, 22, 2018)
        | _is_specific_date(year_week, 11, 28, 2019)
        | _is_specific_date(year_week, 11, 26, 2020)
    )
    return thanksgiving


def _is_specific_date(year_week: pd.Series, month: int, day: int, year: int = None) -> pd.Series:
    if year is None:
        dates = pd.Series(
            [dt.datetime(i, month, day) for i in set(year_week.apply(datetime_module.get_calendar_year_from_year_index))]
        )
    else:
        dates = pd.Series([dt.datetime(year, month, day)])
    year_weeks_end_of_year = datetime_module.get_year_week_from_date(dates=dates)
    return year_week.isin(year_weeks_end_of_year).astype(int)


def _is_end_of_year_week(year_week: pd.Series) -> pd.Series:
    last_days_of_year = pd.Series(
        [
            dt.datetime(i, 12, 31) - timedelta(days=k)
            for i in set(year_week.apply(datetime_module.get_calendar_year_from_year_index))
            for k in range(4)
        ]
    )
    year_weeks_end_of_year = last_days_of_year.apply(datetime_module.to_isocalendar_year_week)
    return year_week.isin(year_weeks_end_of_year).astype(int)


def _is_week_between(year_week: pd.Series, week_start: int, week_end: int) -> pd.Series:
    weeks = year_week.mod(100)
    return weeks.between(week_start, week_end, inclusive="both").astype(int)


def _is_n_week_before_last_week(year_week: pd.Series, n_before: int) -> pd.Series:
    """Flags weeks corresponding to n week before the last one of the year"""
    years, weeks = year_week // 100, year_week.mod(100)
    nb_weeks_in_year = years.apply(datetime_module.get_nb_weeks_in_year)
    return (weeks == (nb_weeks_in_year - n_before)).astype(int)


def _compute_week_in_month_cosinus(year_week: pd.Series) -> pd.Series:
    """gives a 'feeling' of the position of the Monday within the month."""
    monday = year_week.apply(datetime_module.get_monday_timestamp)
    week_in_month = np.cos(2 * np.pi * monday.dt.day / 31)
    return week_in_month

'''
def add_monthly_seasonality(df: pd.DataFrame) -> pd.DataFrame:
    """Adds months as new columns and flag each row by the month the most represented in the week"""
    # If week starts on Sunday, middle of week is Wednesday
    middle_day = "wednesday" if model_settings.IS_WEEK_START_SUNDAY else "thursday"
    get_year_week_middle_timestamp = partial(get_year_week_day_timestamp, day_name=middle_day)
    features = df.year_week.apply(get_year_week_middle_timestamp).dt.month
    features = pd.get_dummies(features)
    features.columns = n.MONTHS_LIST
    return pd.concat([df, features], axis=1)
'''


def add_quarterly_seasonality(year_week: pd.Series, quarter: int) -> pd.DataFrame:
    assert (quarter >= 1) and (quarter <= 4)
    quarter_first_week = 13 * (quarter - 1) + 1
    _, weeks = datetime_module.parse_year_index(year_week)
    return weeks.between(quarter_first_week, quarter_first_week + 13).astype(int)


def construct_seasonality_and_event_features(
    features_df: pd.DataFrame
    #relevant_features = None: List[str],
    #additional_events: Tuple[Tuple[str, Union[Tuple[int, int], None]]],
) -> pd.DataFrame:

    _FEATURE_BUILDERS = {
        "christmas_season": partial(_is_week_between, week_start=48, week_end=53),
        "easter": _is_easter_year_week,
        "is_antepenultimate_week": partial(_is_n_week_before_last_week, n_before=2),
        "is_penultimate_week": partial(_is_n_week_before_last_week, n_before=1),
        "is_last_week": partial(_is_n_week_before_last_week, n_before=0),
        "is_week_51": partial(_is_week_between, week_start=51, week_end=51),
        "is_week_01": partial(_is_week_between, week_start=1, week_end=1),
        "is_year_end_week": _is_end_of_year_week,
        "is_pay_day": _is_pay_day_events,
        "is_holidays": _is_golden_week_holidays,
        "is_saint_patrick": _is_saint_patrick,
        "st_patrick_off_grocery": _is_st_patrick_off_grocery,
        "st_patrick_off_liquor": _is_st_patrick_off_liquor,
        "st_patrick_off_nabca": _is_st_patrick_off_nabca,
        "first_week2019_off_nabca": _is_first_week2019_off_nabca,
        "week52_2020_off_nabca": _is_week52_2020_off_nabca,
        "second_week": _is_second_week,
        "fourth_july": _is_4th_july,
        "halloween": _is_halloween,
        "thanksgiving": _thanksgiving,
        "cinco_mayo": _is_cinco_mayo,
        "father_day": _is_father_day,
        "first_quarter": partial(add_quarterly_seasonality, quarter=1),
        "second_quarter": partial(add_quarterly_seasonality, quarter=2),
        "third_quarter": partial(add_quarterly_seasonality, quarter=3),
        "week_month_number": _compute_week_in_month_cosinus,
        "is_first_week_month": _is_first_week_of_the_month,
        "is_end_summer": partial(_is_week_between, week_start=32, week_end=34),
    }

    #additional_event_features = additional_events.keys()
    features_df["week"] = features_df["year_week"] % 100


    for feature in _FEATURE_BUILDERS:

        #if feature in additional_event_features:
        #    weeks = [weeks for f, weeks in additional_events.items() if f == feature]
        #    weeks = weeks.pop() if weeks else None

        if feature in _FEATURE_BUILDERS:
            features_df[feature] = _FEATURE_BUILDERS[feature](year_week=features_df["year_week"])

        #else:
        #    features_df[feature] = features_df["week"].between(*weeks, inclusive="both").astype(int)

    #if set(relevant_features).intersection(n.MONTHS_LIST):
    #    features_df = add_monthly_seasonality(features_df)

    features_df = features_df.drop(columns={"week"})

    return features_df

