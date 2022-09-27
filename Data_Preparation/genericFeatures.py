'''
Current status of development - V01:

DONE
- create_feature_as_gap_to_brand_reference_level

TO BE DONE
/

'''

from typing import Tuple

import numpy as np
import pandas as pd

# from matrix.st_response_model.feature_engineering.utils import get_grouping_columns

def create_feature_as_gap_to_brand_reference_level(
    feature_df: pd.DataFrame,
    col_feature: str,
    col_feature_ref: str = None,
    group: str = None,
    is_ratio_to_ref: bool = False,
    quantile_reference: float = 0.1,
    force_positive_feature: bool = False,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Function to transform a feature in absolute value to a gap with a reference level for that feature

    Assumptions:
    - The reference level is computed at brand level as a quantile of all available historical values
    - It is a proxy of a normal situation if PR were to do no activation on that touchpoint

    This function aims at filtering out the unexplained baseline (bulk) impact and keep the residual
    impact only; it would too strong of an assumption to extrapolate to a situation we have never
    seen in the past (e.g. zero price, no on-trade visibility, etc.)

    Args:
        feature_df:
        col_feature: Name of the feature to transform
        col_feature_ref: Name of reference column in the output. If column is None, the reference
            feature is not returned in the output table
        quantile_reference: quantile used to compute the reference price
        force_positive_feature:
        is_ratio_to_ref:
        channel_suffix:

    Returns:
        - feature_df: table with the residual feature that we will use in the model
        - feature_bulk_df: table with bulk of feature that was filtered out
    """
    assert (quantile_reference >= 0) & (quantile_reference <= 1)
    #relevant_granularity = get_grouping_columns()
    #keys = [key for key in relevant_granularity if key != n.F_YEAR_WEEK]
    #logger.info(f"[FEATURES] Building `{col_feature}` feature as a gap to reference level")

    # 1. Compute the feature reference level
    #is_ref_column_returned = bool(col_feature_ref)
    col_feature_ref = "_".join([col_feature, "ref"]) if not col_feature_ref else col_feature_ref

    #returns the quantile at level "quantile_reference" for each group (brand)
    ref_df = feature_df.groupby(group)[col_feature].quantile(q=quantile_reference).rename(col_feature_ref)

    # 2. Compute gap to reference level (forced to be positive)
    feature_df = feature_df.merge(ref_df, on=group, how="inner")
    #feature_df[col_feature + "_raw"] = feature_df[col_feature].copy()
    feature_df[col_feature] = feature_df[col_feature] - feature_df[col_feature_ref]
    #feature_raw = feature_df[col_feature + "_raw"].sum()

    # 3. Clip to force gap to be positive
    if force_positive_feature:
        #logger.info(f"[FEATURES] Negative values of `{col_feature}` are capped to 0")
        feature_df[col_feature] = feature_df[col_feature].clip(0)

    # 4. Compute bulk of feature that was filtered out (must be kept for spends)
    # feature_bulk_df = feature_df[relevant_granularity + [col_feature]].copy()
    # feature_bulk_df[col_feature] = feature_df[col_feature + "_raw"] - feature_bulk_df[col_feature]
    # feature_check = feature_bulk_df[col_feature].sum() + feature_df[col_feature].sum()
    # assert np.abs(feature_raw - feature_check) <= 10 ** (-3)

    # 5. Compute feature as a discount / gap ratio vs the reference
    if is_ratio_to_ref:
        #logger.info(f"[FEATURES] `{col_feature}` feature computed as ratio to reference level")
        feature_df[col_feature] = feature_df[col_feature] / feature_df[col_feature_ref].replace(0, 1)

    # if not is_ref_column_returned:
    #     feature_df = feature_df.drop(columns=[col_feature_ref])

    return feature_df
