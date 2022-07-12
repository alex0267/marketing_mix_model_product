import seasonality
import promotion
import testing
import pandas as pd

#import data - we define a list of unique weeks that are subject to event & seasonality engineering
media_exec_df = pd.read_csv('data/FRA_SPEND_MEDIA_EXECUTION_MAPPING.csv')
unique_weeks = pd.DataFrame(media_exec_df['YEAR_WEEK'].unique())
unique_weeks = unique_weeks.rename(columns={0:'year_week'})

sell_out_df = pd.read_csv('data/FRA_SELL_OUT_COMPANY_MAPPING.csv')
sell_out_competition_df = pd.read_csv('data/FRA_SELL_OUT_COMPETITORS_MAPPING.csv')

def run():

    #calculate event & seasonality features
    features_df = seasonality.construct_seasonality_and_event_features(
        unique_weeks
    )

    #calculate promotion feature with 0.9 percentile reference level
    promo = promotion.compute_price_discount_feature(sell_out_df, quantile_reference=0.9)

    #calculate competiton feature based on category
    #comp = testing.construct_price_competitors_feature(sell_out_competition_df)

    features_df.to_csv("seasonality_features.csv")
    promo.to_csv("promo.csv")

    return features_df

run()