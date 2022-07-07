import seasonality
import pandas as pd

#import data - we define a list of unique weeks that are subject to event & seasonality engineering
df = pd.read_csv('data/FRA_SPEND_MEDIA_EXECUTION_MAPPING.csv')
unique_weeks = pd.DataFrame(df['YEAR_WEEK'].unique())
unique_weeks = unique_weeks.rename(columns={0:'year_week'})


def run():
    print(unique_weeks)

    #add event & seasonality features
    features_df = seasonality.construct_seasonality_and_event_features(
        unique_weeks
        #relevant_features=model_settings.seasonality_features,
        #additional_events=model_settings.SEASONALITY_VARIABLES_EVENTS,
    )

    features_df.to_csv("seasonality_features.csv")

    return features_df

run()