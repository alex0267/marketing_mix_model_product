import seasonality


def run():

    features_df = seasonality.construct_seasonality_and_event_features(
        features_df,
        relevant_features=model_settings.seasonality_features,
        additional_events=model_settings.SEASONALITY_VARIABLES_EVENTS,
    )

    print("hi")

    return 0