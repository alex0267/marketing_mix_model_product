from math import dist
import pandas as pd
import DATA_PREPARATION.genericFeatures

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
    #distribution_df = distribution_df[distribution_df['BRAND']==configurations['BRANDS'][0]]
    distribution_df = distribution_df[['BRAND', 'YEAR_WEEK', 'DISTRIBUTION']].rename(columns={'DISTRIBUTION':'distribution'})

    # Distribution feature as gap to a reference level if a quantile level is given as an input
    if quantile_reference_level is not None:
        distribution_df = DATA_PREPARATION.genericFeatures.create_feature_as_gap_to_brand_reference_level(
            feature_df=distribution_df,
            col_feature='distribution',
            col_feature_ref='DISTRIBUTION_REF',
            group='BRAND',
            quantile_reference=quantile_reference_level,
            force_positive_feature=False,
            is_ratio_to_ref=True,
        )


    return distribution_df

def construct_off_trade_visibility_feature(
    sell_out_distribution_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Execution of off-trade visibility = weighted distribution of displays (e.g. in Nielsen PRD)

    Assumption: Filter on right channels is done outside of this function
    e.g. in Germany / Japan, keeping only "OFF" distribution_code as a proxy for the global distribution
    """

    relevant_columns = [
        'DISTRIBUTION_FEATURE_DISPLAY',
        'DISTRIBUTION_DISPLAY',
    ]
    

    distribution_df = sell_out_distribution_df.copy()

    #distribution_df = distribution_df[relevant_columns].max()
    distribution_df["off_trade_visibility"] = distribution_df[relevant_columns].fillna(0).sum(axis=1)
    distribution_df = distribution_df[['BRAND', 'YEAR_WEEK','off_trade_visibility']]


    return distribution_df