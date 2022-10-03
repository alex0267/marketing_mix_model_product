import pandas as pd
from generic_features import create_feature_as_gap_to_brand_reference_level
from math import dist

def construct_distribution_feature(
    sell_out_distribution_df: pd.DataFrame,
    configurations,
    quantile_reference_level: float = None
    
):
    """
    Args:
        sell_out_distribution_df:

        quantile_reference_level:
    Returns:
    Distribution level per brand and week
    """

    distribution_df = sell_out_distribution_df.copy()
    # distribution_df = distribution_df[distribution_df['BRAND']==configurations['BRANDS'][0]]
    distribution_df = distribution_df[['BRAND', 'YEAR_WEEK', 'DISTRIBUTION']]


    # Distribution feature as gap to a reference level if a quantile level is given as an input
    if quantile_reference_level is not None:
        distribution_df = create_feature_as_gap_to_brand_reference_level(
            feature_df=distribution_df,
            col_feature='DISTRIBUTION',
            col_feature_ref='DISTRIBUTION_REF',
            group = "BRAND",
            quantile_reference=quantile_reference_level,
            force_positive_feature=False,
            is_ratio_to_ref=True,
        )

    return distribution_df
    