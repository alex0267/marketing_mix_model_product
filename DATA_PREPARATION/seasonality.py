" All seasonality & events related features """
'''
Current status of development - V01:

See here: https://docs.google.com/spreadsheets/d/1fJwTlJimAz0p-UOnU5KAdRiDrSY5JzNhq0kqGOzqF68/edit#gid=0

'''
import DATA_PREPARATION.datetimeModule
import datetime as dt
from datetime import timedelta
from functools import partial
from typing import List, Tuple, Union

import numpy as np
import pandas as pd
from dateutil.easter import easter


def _is_n_week_before_last_week(year_week: pd.Series, n_before: int) -> pd.Series:
    """Flags weeks corresponding to n week before the last one of the year"""
    years, weeks = year_week // 100, year_week.mod(100)
    nb_weeks_in_year = years.apply(DATA_PREPARATION.datetimeModule.get_nb_weeks_in_year)
    return (weeks == (nb_weeks_in_year - n_before)).astype(int)


def add_monthly_seasonality(df: pd.DataFrame) -> pd.DataFrame:
    """Adds months as new columns and flag each row by the month the most represented in the week"""
    # If week starts on Sunday, middle of week is Wednesday
    #middle_day = "wednesday" if model_settings.IS_WEEK_START_SUNDAY else "thursday"
    middle_day = "wednesday"
    get_year_week_middle_timestamp = partial(DATA_PREPARATION.datetimeModule.get_year_week_day_timestamp, day_name=middle_day)
    features = df.YEAR_WEEK.apply(get_year_week_middle_timestamp).dt.month
    features = pd.get_dummies(features)
    features.columns = [
                        "is_january",
                        "is_february",
                        "is_march",
                        "is_april",
                        "is_may",
                        "is_june",
                        "is_july",
                        "is_august",
                        "is_september",
                        "is_october",
                        "is_november",
                        "is_december",
                        ]
    return pd.concat([df, features], axis=1)




def construct_seasonality_and_event_features(
    features_df: pd.DataFrame
    #relevant_features = None: List[str],
    #additional_events: Tuple[Tuple[str, Union[Tuple[int, int], None]]],
) -> pd.DataFrame:

    _FEATURE_BUILDERS = {

        "is_last_week": partial(_is_n_week_before_last_week, n_before=0)

    }



    for feature in _FEATURE_BUILDERS:


        if feature in _FEATURE_BUILDERS:
            features_df[feature] = _FEATURE_BUILDERS[feature](year_week=features_df["YEAR_WEEK"])


    features_df = add_monthly_seasonality(features_df)

    return features_df

