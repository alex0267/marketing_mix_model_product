from typing import Optional
import pandas as pd

from DATA_PREPARATION.genericFeatures import create_feature_as_gap_to_brand_reference_level

def add_loyalty_card(
    promotion_df: pd.DataFrame, distribution_df: pd.DataFrame, col_feature: str, coef:float
) -> pd.DataFrame:
    """
    Function to add the loyalty card distribution to the discount feature.
    It modifies the F_PRICE_DISCOUNT_FEATURE column by adding the loyal card distribution with a parameter coefficient.
    Args:
    - promotion_df
    - distribution_df
    - coef - normally at 1

    Returns:
    - promotion_df: same df but with modified column col_feature
    """

    if coef < 0:
        return promotion_df

    promotion_df = promotion_df.merge(
        distribution_df[["BRAND", "YEAR_WEEK", "DISTRIBUTION_PROMO"]],
        on=["BRAND", "YEAR_WEEK"],
        how="left",
    )

    promotion_df[col_feature] = promotion_df[col_feature] + coef * promotion_df["DISTRIBUTION_PROMO"] / 1000
    promotion_df = promotion_df.drop(columns="DISTRIBUTION_PROMO")

    
    return promotion_df

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
    promotion_df: pd.DataFrame,
    distribution_df: pd.DataFrame,
    configurations,
    quantile_reference: float,
) -> pd.DataFrame:
    """
    Relative apparent discount compared to the baseline price defined as xth percentile of
    observed average prices (where x = quantile_reference * 100)

    Price influenced by product & distribution channel mixes
    """


    promotion_df["PRICE_ASP"] = promotion_df["SALES_SO"] / promotion_df["VOLUME_SO"]
    start = promotion_df['YEAR_WEEK'].iloc[0]
    end = promotion_df['YEAR_WEEK'].iloc[-1]

    #calculate the price period to base the relative gap to 90th price on it
    promotion_df['PRICE_PERIOD'] = promotion_df['YEAR_WEEK'].apply(
    lambda year_week: assign_period(
        year_week,
        start,
        end,
        configurations['PRICE_PERIOD_1_END'],
        configurations['PRICE_PERIOD_2_END'],
    )
    )


    col_feature = "relative_gap_to_90th_price"
    promotion_df[col_feature] = promotion_df["PRICE_ASP"].copy()
    promotion_df = create_feature_as_gap_to_brand_reference_level(
        feature_df=promotion_df,
        col_feature=col_feature,
        col_feature_ref="ref_90th_price",
        group = ["BRAND","PRICE_PERIOD"],
        quantile_reference=quantile_reference,
        is_ratio_to_ref=True,
        force_positive_feature=False,
    )



    # multiplication of columns *-1 to reverse the promotion logic
    # -> increasing ratio = increasing sales (by increasing promotion)
    promotion_df[col_feature] = promotion_df[col_feature] * (-1)

    #the promotion is influenced by the loyality card (getting points for buying specific things)
    #The existance of a loyalty card in a specific week for a specific brand (nielsen proxy distribution)
    #affects promotional activities

    promotion_df = add_loyalty_card(promotion_df, distribution_df, col_feature, coef =1)
    
    promotion_df = promotion_df.rename(columns={"VOLUME_SO": "TARGET_VOL_SO", "relative_gap_to_90th_price": "promotion"})


    return promotion_df

