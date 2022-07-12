# import logging

import pandas as pd

# from matrix.data_manager import names as n
# from matrix.st_response_model.feature_engineering.features.price_discount import (
#     compute_price_discount_feature,
# )
# from matrix.st_response_model.feature_engineering.utils import get_grouping_columns
# from matrix.st_response_model.model_settings import model_settings

#logger = logging.getLogger(__name__)


def construct_price_competitors_feature(
    sell_out_competitors_df: pd.DataFrame
        # , price_df: pd.DataFrame, channel: str
) -> pd.DataFrame:

    #grouped_columns = get_grouping_columns()
    #relevant_columns = grouped_columns + [n.F_COMPETITORS_PRICE_FEATURE]

    #if sell_out_competitors_df.empty:
        #logger.warning("Ignoring competitors sell-out price feature (empty table)")
        #return pd.DataFrame(columns=relevant_columns)

    competition_mapping_df = pd.DataFrame.from_records(
        model_settings.MAPPING_BRANDS_COMPETITORS[channel],
        columns=[n.F_BRAND, n.F_BRAND_COMPETITOR, n.F_SUB_BRAND_COMPETITOR, n.F_CATEGORY],
    )

    # Get mapping of main competitors per PR brand
    sell_out_competitors_df = _filter_sub_brands(
        sell_out_competitors_df=sell_out_competitors_df,
        competition_mapping_df=competition_mapping_df,
    )

    # Aggregate all at model granularity and keep sums of Volume and sales for each PR brand
    sell_out_competitors_df = (
        sell_out_competitors_df.groupby(by=grouped_columns)[[n.F_VOLUME_SO, n.F_SALES_SO]].sum().reset_index()
    )

    # Compute competition feature
    if model_settings.COMPETITORS_FEATURE_AS_DISCOUNT:
        price_competitors_df = compute_price_competitors_feature_as_discount(
            sell_out_competitors_df=sell_out_competitors_df
        )
    else:
        price_competitors_df = _compute_price_competitors_feature(
            sell_out_competitors_df=sell_out_competitors_df,
            price_df=price_df,
        )

    return price_competitors_df[relevant_columns].copy()


def compute_price_competitors_feature_as_discount(
    sell_out_competitors_df: pd.DataFrame,
) -> pd.DataFrame:
    price_competitors_df = compute_price_discount_feature(
        sell_out_pr_agg_df=sell_out_competitors_df,
        quantile_reference=0.9,
    )
    price_competitors_df = price_competitors_df.rename(
        columns={
            n.F_PRICE_DISCOUNT_FEATURE: n.F_COMPETITORS_PRICE_FEATURE,
            "ref_90th_price": "ref_90th_price_comp",
        }
    )
    regional_columns = [n.F_REGION, n.F_REGION_GROUP] if model_settings.REGIONAL_MODEL else []

    return price_competitors_df[
        list(model_settings.RESPONSE_LEVEL) + regional_columns + [n.F_COMPETITORS_PRICE_FEATURE]
    ]


def _compute_price_competitors_feature(
    sell_out_competitors_df: pd.DataFrame, price_df: pd.DataFrame
) -> pd.DataFrame:

    grouped_columns = get_grouping_columns()
    sell_out_competitors_df = sell_out_competitors_df.copy()

    if not model_settings.REGIONAL_MODEL:
        sales = sell_out_competitors_df[n.F_SALES_SO]
        volume = sell_out_competitors_df[n.F_VOLUME_SO]
    else:
        sales = sell_out_competitors_df.groupby([n.F_BRAND, n.F_YEAR_WEEK, n.F_REGION_GROUP])[
            n.F_SALES_SO
        ].transform("sum")
        volume = sell_out_competitors_df.groupby([n.F_BRAND, n.F_YEAR_WEEK, n.F_REGION_GROUP])[
            n.F_VOLUME_SO
        ].transform("sum")
    sell_out_competitors_df[n.F_COMPETITORS_PRICE_ASP] = sales / volume

    # Add competitors price in main price table
    price_competitors_df = price_df.merge(
        sell_out_competitors_df[grouped_columns + [n.F_COMPETITORS_PRICE_ASP]],
        how="left",
        on=grouped_columns,
    )

    # Calculate discount to PR price
    price_competitors_df[n.F_COMPETITORS_PRICE_FEATURE] = (
        price_competitors_df[n.F_PRICE_ASP] - price_competitors_df[n.F_COMPETITORS_PRICE_ASP]
    ) / price_competitors_df[n.F_PRICE_ASP]

    return price_competitors_df


def _filter_sub_brands(
    sell_out_competitors_df: pd.DataFrame, competition_mapping_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Keep only sub-brands as defined in the the competition brand mapping
    """

    sell_out_competitors_df = sell_out_competitors_df.copy()
    sell_out_competitors_df = sell_out_competitors_df.rename(columns={n.F_BRAND: n.F_BRAND_COMPETITOR})

    sell_out_competitors_df = sell_out_competitors_df.merge(
        competition_mapping_df, how="right", on=[n.F_CATEGORY, n.F_BRAND_COMPETITOR]
    )

    # Filter on sub brands
    #   - keep all sub brands when field is empty
    #   - otherwise keep only defined sub brand
    sell_out_competitors_df[n.F_SUB_BRAND_COMPETITOR] = sell_out_competitors_df[
        n.F_SUB_BRAND_COMPETITOR
    ].where(
        sell_out_competitors_df[n.F_SUB_BRAND_COMPETITOR].notnull(), sell_out_competitors_df[n.F_SUB_BRAND]
    )

    sell_out_competitors_df = sell_out_competitors_df.loc[
        sell_out_competitors_df[n.F_SUB_BRAND_COMPETITOR] == sell_out_competitors_df[n.F_SUB_BRAND]
    ].copy()

    return sell_out_competitors_df
