import datetime as dt
from typing import List, Optional, Tuple, Union

#import numpy as np
import pandas as pd

#import names as n
#from matrix.st_response_model.model_settings import model_settings


def get_year_week_from_date(dates: pd.Series):
    """
    Return iso-calendar year_week number (consistent with Nielsen definition) assuming the
    assuming the week starts on:
    - Sunday whenever `model_settings.IS_WEEK_START_SUNDAY` = True
    - Monday whenever `model_settings.IS_WEEK_START_SUNDAY` = False
    """

    #if model_settings.IS_WEEK_START_SUNDAY:
    #    dates = dates + np.timedelta64(1, "D")

    return dates.dt.strftime("%G%V").astype(int)


def parse_year_index(
    year_index: Union[int, pd.Series]
) -> Union[Tuple[int, int], Tuple[pd.Series, pd.Series]]:
    return year_index // 100, year_index % 100


def to_isocalendar_year_week(timestamp: dt.datetime) -> int:
    return int(timestamp.strftime("%G%V"))


def to_year_month(timestamp: dt.datetime) -> int:
    return timestamp.year * 100 + timestamp.month


def get_monday_timestamp(year_week: int) -> dt.datetime:
    year, week = parse_year_index(year_index=year_week)
    return dt.datetime.fromisocalendar(year=year, week=week, day=1)


def year_week_difference(year_week_start: int, year_week_end: int) -> int:
    return int(
        (get_monday_timestamp(year_week_end) - get_monday_timestamp(year_week_start)) / dt.timedelta(days=7)
    )


def shift_year_week(year_week: int, weeks: int) -> int:
    week_monday_timestamp = get_monday_timestamp(year_week)
    return to_isocalendar_year_week(week_monday_timestamp + dt.timedelta(weeks=weeks))


def generate_year_week_range(year_week_start: int, length: int, forward: bool) -> List[int]:
    sign = 1 if forward else -1
    return sorted([shift_year_week(year_week=year_week_start, weeks=sign * i) for i in range(length)])


def get_fiscal_year_from_year_week(year_week: int) -> int:
    year, week = parse_year_index(year_index=year_week)
    if week > 26:
        return year + 1
    return year


def get_fiscal_year_from_year_month(year_month: int) -> int:
    year, month = parse_year_index(year_index=year_month)
    if month > 6:
        return year + 1
    return year


def get_calendar_year_from_year_index(year_index: int) -> int:
    year, _ = parse_year_index(year_index=year_index)
    return year


def get_complete_years_from_year_week(year_week: pd.Series, is_fiscal_year: Optional[bool] = False) -> List:
    """
    Returns a list of complete years in year_week (with at least every weeks in the year represented)
    """
    yw_converter = get_fiscal_year_from_year_week if is_fiscal_year else get_calendar_year_from_year_index
    year_week_count_map = year_week.drop_duplicates().apply(yw_converter).value_counts().to_dict()

    return [
        year
        for year, week_count in year_week_count_map.items()
        if week_count >= get_nb_weeks_in_year(year=year, is_fiscal_year=is_fiscal_year)
    ]

'''
def get_advanced_calendar_year_month_from_year_week(
    df: pd.DataFrame, ind_cols: List[str], value_cols: List[str], agg_type: str = "sum"
) -> pd.DataFrame:
    """
    Resample weekly data at the daily level, and aggregate back at the montlhy level

    Args:
        df: input DataFrame, containing weekly data (and year_week column)
        ind_cols: index columns, by which the data will be grouped (typically, ["brand"])
        value_cols: columns that will be aggregated from weekly to monthly level
        agg_type: aggregation type, should be in ["sum", "mean", "count"]
    """

    if agg_type not in ["sum", "mean", "count"]:
        raise NotImplementedError(
            "Weekly to monthly only implemented for sum, mean and count, tyring to apply " + agg_type
        )

    # Filter columns of the input DataFrame
    filtered_df = df[ind_cols + value_cols + [n.F_YEAR_WEEK]].copy()
    filtered_df[n.F_YEAR_WEEK] = filtered_df[n.F_YEAR_WEEK].astype(int)

    # Get last week of each group
    end_weeks = filtered_df.groupby(ind_cols, as_index=False)[[n.F_YEAR_WEEK]].max()

    # Get week after last week
    end_weeks[n.F_YEAR_WEEK] = end_weeks[n.F_YEAR_WEEK].map(lambda x: shift_year_week(x, 1))

    filtered_df = pd.concat([filtered_df, end_weeks], sort=False)

    filtered_df.fillna({col: 0 for col in value_cols}, inplace=True)

    resampled_df = filtered_df.copy()
    resampled_df["day"] = resampled_df[n.F_YEAR_WEEK].map(get_monday_timestamp)
    resampled_df = resampled_df.set_index("day")
    resampled_df = resampled_df.groupby(ind_cols).resample("d").ffill(limit=6)  # Fillna limited to 1 week
    resampled_df.drop(columns=ind_cols, inplace=True)
    resampled_df.reset_index(inplace=True)

    if agg_type == "sum":
        resampled_df[value_cols] = resampled_df[value_cols] / 7
        for col in value_cols:
            assert int(resampled_df[col].sum()) == int(filtered_df[col].sum())

    elif agg_type in ["mean", "count"]:
        pass

    # Get year month from day
    resampled_df[n.F_YEAR_MONTH] = resampled_df["day"].apply(to_year_month)

    if agg_type == "sum":
        monthly_df = resampled_df.groupby(ind_cols + [n.F_YEAR_MONTH])[value_cols].sum().reset_index()
        for col in value_cols:
            assert int(monthly_df[col].sum()) == int(filtered_df[col].sum())

    elif agg_type == "mean":
        monthly_df = resampled_df.groupby(ind_cols + [n.F_YEAR_MONTH])[value_cols].mean().reset_index()

    elif agg_type == "count":
        monthly_df = resampled_df.groupby(ind_cols + [n.F_YEAR_MONTH])[value_cols].count().reset_index()

    return monthly_df
'''

def get_weeks_after(first_week: int, number_of_weeks: int) -> List:
    first_monday = get_monday_timestamp(first_week)
    weeks = pd.date_range(start=first_monday, periods=number_of_weeks, freq="W-MON")

    return list(get_year_week_from_date(pd.Series(weeks)))


def filter_time_span(
    df: pd.DataFrame, time_start: str, time_end: str, time_column: str = "year_week"
) -> pd.DataFrame:
    return df[(df[time_column] >= time_start) & (df[time_column] <= time_end)]


def contains_month_day_in_year_week(year_week: int, day: int) -> bool:
    year, week = parse_year_index(year_index=year_week)
    week_monday = dt.datetime.fromisocalendar(year=year, week=week, day=1)
    week_days = [(week_monday + dt.timedelta(days=i)).day for i in range(7)]
    return day in week_days


def get_nb_weeks_in_year(year: int, is_fiscal_year: Optional[bool] = False) -> int:
    """
    Returns the number of ISO weeks for the provided year. According to the ISO definition, December 28th
    will be always in the last week of the year. If the year is fiscal, then the number of weeks depends on
    the number of weeks in the last year (because a fiscal year is looking backward in time)
    """
    if is_fiscal_year:
        year -= 1
    _, last_week, _ = dt.date(year, 12, 28).isocalendar()
    return last_week


def get_iso_day_number(day_name: str) -> int:
    """Returns day index corresponding to the position of the day in the week according to ISO definition"""
    day_names_to_numbers = {
        "monday": 1,
        "tuesday": 2,
        "wednesday": 3,
        "thursday": 4,
        "friday": 5,
        "saturday": 6,
        "sunday": 7,
    }
    try:
        return day_names_to_numbers[day_name.lower()]
    except KeyError:
        raise KeyError(f"Incorrect week day name: {day_name}") from None


def get_year_week_day_timestamp(year_week: int, day_name: str) -> dt.datetime:
    """
    Extracts a date from a single year_week (int) by selecting a specific day in the week
    """
    year, week = parse_year_index(year_index=year_week)
    iso_day_nb = get_iso_day_number(day_name=day_name)
    return dt.datetime.fromisocalendar(year=year, week=week, day=iso_day_nb)

'''
def get_start_end_year_weeks_from_year(year: int, is_fiscal_year: bool) -> (int, int):
    start_year_week = (year - 1) * 100 + 27 if is_fiscal_year else year * 100 + 1
    end_year_week = year * 100 + 26 if is_fiscal_year else year * 100 + get_nb_weeks_in_year(year)

    return start_year_week, end_year_week


YEAR_WEEK_TO_YEAR_CONVERTERS = {
    n.F_YEAR_CALENDAR: get_calendar_year_from_year_index,
    n.F_YEAR_FISCAL: get_fiscal_year_from_year_week,
}
'''