" All seasonality & events related features """
'''
Current status of development - V01:

See here: https://docs.google.com/spreadsheets/d/1fJwTlJimAz0p-UOnU5KAdRiDrSY5JzNhq0kqGOzqF68/edit#gid=0

'''
import datetime as dt
import numpy as np
import pandas as pd

from datetime_module import get_nb_weeks_in_year, get_year_week_day_timestamp
from functools import partial


def _is_n_week_before_last_week(year_week: pd.Series, n_before: int) -> pd.Series:
    """Flags weeks corresponding to n week before the last one of the year"""
    years, weeks = year_week // 100, year_week.mod(100)
    nb_weeks_in_year = years.apply(get_nb_weeks_in_year)
    return (weeks == (nb_weeks_in_year - n_before)).astype(int)


def add_monthly_seasonality(df: pd.DataFrame) -> pd.DataFrame:
    """Adds months as new columns and flag each row by the month the most represented in the week"""
    # If week starts on Sunday, middle of week is Wednesday
    #middle_day = "wednesday" if model_settings.IS_WEEK_START_SUNDAY else "thursday"
    middle_day = "wednesday"
    get_year_week_middle_timestamp = partial(get_year_week_day_timestamp, day_name=middle_day)
    features = df.YEAR_WEEK.apply(get_year_week_middle_timestamp).dt.month
    features = pd.get_dummies(features)
    features.columns = [
                        "IS_JANUARY",
                        "IS_FEBRUARY",
                        "IS_MARCH",
                        "IS_APRIL",
                        "IS_MAY",
                        "IS_JUNE",
                        "IS_JULY",
                        "IS_AUGUST",
                        "IS_SEPTEMBER",
                        "IS_OCTOBER",
                        "IS_NOVEMBER",
                        "IS_DECEMBER",
                        ]
    return pd.concat([df, features], axis=1)


def construct_seasonality_and_event_features(
    features_df: pd.DataFrame
) -> pd.DataFrame:

    _FEATURE_BUILDERS = {
        # "christmas_season": partial(_is_week_between, week_start=48, week_end=53),
        # "easter": _is_easter_year_week,
        # "is_antepenultimate_week": partial(_is_n_week_before_last_week, n_before=2),
        # "is_penultimate_week": partial(_is_n_week_before_last_week, n_before=1),
        "is_last_week": partial(_is_n_week_before_last_week, n_before=0),
        # "is_week_51": partial(_is_week_between, week_start=51, week_end=51),
        # "is_week_01": partial(_is_week_between, week_start=1, week_end=1),
        # "is_year_end_week": _is_end_of_year_week,
        # "is_pay_day": _is_pay_day_events,
        # "is_holidays": _is_golden_week_holidays,
        # "is_saint_patrick": _is_saint_patrick,
        # "second_week": _is_second_week,
        # "fourth_july": _is_4th_july,
        # "halloween": _is_halloween,
        # "thanksgiving": _thanksgiving,
        # "cinco_mayo": _is_cinco_mayo,
        # "father_day": _is_father_day,
        # "first_quarter": partial(add_quarterly_seasonality, quarter=1),
        # "second_quarter": partial(add_quarterly_seasonality, quarter=2),
        # "third_quarter": partial(add_quarterly_seasonality, quarter=3),
        # "week_month_number": _compute_week_in_month_cosinus,
        # "is_first_week_month": _is_first_week_of_the_month,
        # "is_end_summer": partial(_is_week_between, week_start=32, week_end=34),
    }

    for feature in _FEATURE_BUILDERS:
        if feature in _FEATURE_BUILDERS:
            features_df[feature] = _FEATURE_BUILDERS[feature](year_week=features_df["YEAR_WEEK"])

    features_df = add_monthly_seasonality(features_df)

    return features_df
