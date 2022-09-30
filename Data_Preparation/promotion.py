
'''
Current status of development - V01:

DONE
- Implemented basic price discount feature

TO BE DONE
/

'''

from typing import Optional
import pandas as pd

from Data_Preparation.generic_features import create_feature_as_gap_to_brand_reference_level


def compute_price_discount_feature(
    sell_out_pr_agg_df: pd.DataFrame,
    quantile_reference: float,
) -> pd.DataFrame:
    """
    Relative apparent discount compared to the baseline price defined as xth percentile of
    observed average prices (where x = quantile_reference * 100)

    Price influenced by product & distribution channel mixes
    """

    sell_out_pr_agg_df["PRICE_ASP"] = sell_out_pr_agg_df["SALES_SO"] / sell_out_pr_agg_df["VOLUME_SO"]

    col_feature = "relative_gap_to_90th_price"
    sell_out_pr_agg_df[col_feature] = sell_out_pr_agg_df["PRICE_ASP"].copy()
    sell_out_pr_agg_df = create_feature_as_gap_to_brand_reference_level(
        feature_df=sell_out_pr_agg_df,
        col_feature=col_feature,
        col_feature_ref="ref_90th_price",
        group = "BRAND",
        quantile_reference=quantile_reference,
        is_ratio_to_ref=True,
        force_positive_feature=False,
    )

    # multiplication of columns *-1 to reverse the promotion logic
    # -> increasing ratio = increasing sales (by increasing promotion)
    sell_out_pr_agg_df[col_feature] = sell_out_pr_agg_df[col_feature] * (-1)

    sell_out_pr_agg_df = sell_out_pr_agg_df[["YEAR_WEEK", "BRAND", "VOLUME_SO", "relative_gap_to_90th_price"]]

    return sell_out_pr_agg_df
