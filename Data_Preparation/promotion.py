from typing import Optional
import pandas as pd

from generic_features import create_feature_as_gap_to_brand_reference_level

# def _add_non_promo_sales(sell_out_pr_df: pd.DataFrame) -> pd.DataFrame:
#
#     sell_out_pr_df[n.F_SALES_SO + "_non_promo"] = (
#         sell_out_pr_df[n.F_SALES_SO] - sell_out_pr_df[n.F_SALES_SO_PROMO]
#     ).copy()
#
#     sell_out_pr_df[n.F_VOLUME_SO + "_non_promo"] = (
#         sell_out_pr_df[n.F_VOLUME_SO] - sell_out_pr_df[n.F_VOLUME_SO_PROMO]
#     ).copy()
#
#     return sell_out_pr_df

def compute_price_discount_feature(
    sell_out_pr_agg_df: pd.DataFrame,
    quantile_reference: float,
) -> pd.DataFrame:
    """
    Relative apparent discount compared to the baseline price defined as xth percentile of
    observed average prices (where x = quantile_reference * 100)

    Price influenced by product & distribution channel mixes
    """
    # if not model_settings.REGIONAL_MODEL:
    #     sales = sell_out_pr_agg_df[n.F_SALES_SO]
    #     volume = sell_out_pr_agg_df[n.F_VOLUME_SO]
    # else:
    #     sales = sell_out_pr_agg_df.groupby([n.F_BRAND, n.F_YEAR_WEEK, n.F_REGION_GROUP])[
    #         n.F_SALES_SO
    #     ].transform("sum")
    #     volume = sell_out_pr_agg_df.groupby([n.F_BRAND, n.F_YEAR_WEEK, n.F_REGION_GROUP])[
    #         n.F_VOLUME_SO
    #     ].transform("sum")

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

    return sell_out_pr_agg_df


# def construct_basic_price_discount_feature(
#     sell_out_pr_df: pd.DataFrame,
#     quantile_reference: Optional[float] = 0.9,
# ) -> pd.DataFrame:
#     """
#     Calculate price discount features based on: mix of promo & non-promo sales
#     """
#     # Aggregate sell-out at right granularity
#     relevant_columns = get_grouping_columns()
#     sell_out_pr_agg_df = sell_out_pr_df.groupby(relevant_columns, as_index=False)[
#         [n.F_VOLUME_SO, n.F_SALES_SO]
#     ].sum()
#
#     sell_out_pr_agg_df = compute_price_discount_feature(
#         sell_out_pr_agg_df=sell_out_pr_agg_df,
#         quantile_reference=quantile_reference,
#     )
#     regional_columns = [n.F_REGION, n.F_REGION_GROUP] if model_settings.REGIONAL_MODEL else []
#
#     return sell_out_pr_agg_df[
#         list(model_settings.RESPONSE_LEVEL)
#         + regional_columns
#         + [
#             n.F_VOLUME_SO,
#             n.F_SALES_SO,
#             "relative_gap_to_90th_price",
#             "ref_90th_price",
#             n.F_PRICE_ASP,
#         ]
#     ]
#
#
# def construct_advanced_price_discount_features(
#     sell_out_pr_df: pd.DataFrame, quantile_reference: Optional[float] = 0.9
# ) -> pd.DataFrame:
#     """
#     Calculate price discount features based on:
#         1. mix of promo & non-promo sales
#         2. promo sales only
#         3. non-promo sales only
#
#     Adding spend_promo feature = proxy of promotion spend induced by TPR (deprecated)
#     """
#     sell_out_pr_agg_df = sell_out_pr_df.groupby(list(model_settings.RESPONSE_LEVEL_MAX), as_index=False)[
#         [n.F_VOLUME_SO, n.F_SALES_SO, n.F_SALES_SO_PROMO, n.F_VOLUME_SO_PROMO]
#     ].sum()
#     sell_out_pr_agg_df = _add_non_promo_sales(sell_out_pr_df=sell_out_pr_agg_df)
#
#     asp_df = construct_basic_price_discount_feature(
#         sell_out_pr_df=sell_out_pr_df, quantile_reference=quantile_reference
#     )
#     sell_out_pr_agg_df = sell_out_pr_agg_df.merge(
#         asp_df, on=list(model_settings.RESPONSE_LEVEL_MAX), how="left"
#     )
#
#     for suffix in ["_non_promo", "_promo"]:
#
#         # Discount ratio based on promo & non-promo sales only
#         sell_out_pr_agg_df = compute_price_discount_feature(
#             sell_out_pr_agg_df=sell_out_pr_agg_df,
#             quantile_reference=quantile_reference,
#         )
#         # Discount to common reference ("ref_90th_price_non_promo"), weighted by relative intensity
#         sell_out_pr_agg_df["weighted_discount" + suffix] = (
#             1 - sell_out_pr_agg_df[n.F_PRICE_ASP + suffix] / sell_out_pr_agg_df["ref_90th_price_non_promo"]
#         ) * (sell_out_pr_agg_df[n.F_VOLUME_SO + suffix] / sell_out_pr_agg_df[n.F_VOLUME_SO])
#
#     # Spend induced by TPR
#     sell_out_pr_agg_df = _estimate_promo_spend(
#         sell_out_pr_agg_df=sell_out_pr_agg_df,
#         col_reference_price="ref_90th_price_non_promo",
#     )
#
#     return sell_out_pr_agg_df[
#         list(model_settings.RESPONSE_LEVEL_MAX)
#         + [
#             n.F_VOLUME_SO,
#             n.F_VOLUME_SO_PROMO,
#             n.F_SALES_SO,
#             n.F_SALES_SO_PROMO,
#             n.F_VOLUME_SO + "_non_promo",
#             n.F_PRICE_ASP,
#             n.F_PRICE_ASP + "_promo",
#             n.F_PRICE_ASP + "_non_promo",
#             "ref_90th_price",
#             "relative_gap_to_90th_price",
#             "relative_gap_to_90th_price_promo",
#             "relative_gap_to_90th_price_non_promo",
#             "weighted_discount_promo",
#             "weighted_discount_non_promo",
#             "promo_spend",
#         ]
#     ].copy()
