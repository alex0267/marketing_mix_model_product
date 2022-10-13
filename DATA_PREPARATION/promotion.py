from typing import Optional
import pandas as pd

from DATA_PREPARATION.genericFeatures import create_feature_as_gap_to_brand_reference_level

def assign_period(year_week: int, start: int, end: int, period_1_end: int, period_2_end: int) -> str:
    """
    Function to associate each week to a period.
    It will be used to calculate the price quantile reference level for each period.
    """
    assert (start < period_1_end) & (period_1_end < period_2_end) & (period_2_end < end)
    if year_week <= period_1_end:
        return str(start) + "-" + str(period_1_end)
    elif period_1_end < year_week <= period_2_end:
        return str(period_1_end) + "-" + str(period_2_end)
    else:
        return str(period_2_end) + "-" + str(end)


def compute_price_discount_feature(
    sell_out_pr_agg_df: pd.DataFrame,
    configurations,
    quantile_reference: float,
) -> pd.DataFrame:
    """
    Relative apparent discount compared to the baseline price defined as xth percentile of
    observed average prices (where x = quantile_reference * 100)

    Price influenced by product & distribution channel mixes
    """


    sell_out_pr_agg_df["PRICE_ASP"] = sell_out_pr_agg_df["SALES_SO"] / sell_out_pr_agg_df["VOLUME_SO"]
    start = sell_out_pr_agg_df['YEAR_WEEK'].iloc[0]
    end = sell_out_pr_agg_df['YEAR_WEEK'].iloc[-1]

    #calculate the price period to base the relative gap to 90th price on it
    sell_out_pr_agg_df['PRICE_PERIOD'] = sell_out_pr_agg_df['YEAR_WEEK'].apply(
    lambda year_week: assign_period(
        year_week,
        start,
        end,
        configurations['PRICE_PERIOD_1_END'],
        configurations['PRICE_PERIOD_2_END'],
    )
    )
    print(sell_out_pr_agg_df)
    sell_out_pr_agg_df.to_csv('promo.csv')

    col_feature = "relative_gap_to_90th_price"
    sell_out_pr_agg_df[col_feature] = sell_out_pr_agg_df["PRICE_ASP"].copy()
    sell_out_pr_agg_df = create_feature_as_gap_to_brand_reference_level(
        feature_df=sell_out_pr_agg_df,
        col_feature=col_feature,
        col_feature_ref="ref_90th_price",
        group = ["BRAND","PRICE_PERIOD"],
        quantile_reference=quantile_reference,
        is_ratio_to_ref=True,
        force_positive_feature=False,
    )
    print(sell_out_pr_agg_df)

    sell_out_pr_agg_df.to_excel('promo.xlsx')
    # multiplication of columns *-1 to reverse the promotion logic
    # -> increasing ratio = increasing sales (by increasing promotion)
    sell_out_pr_agg_df[col_feature] = sell_out_pr_agg_df[col_feature] * (-1)

    #sell_out_pr_agg_df = sell_out_pr_agg_df[["YEAR_WEEK", "BRAND", "VOLUME_SO", "relative_gap_to_90th_price"]]

    return sell_out_pr_agg_df

