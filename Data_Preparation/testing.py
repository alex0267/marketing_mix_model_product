import logging
import numpy as np
import pandas as pd

from matrix.data_manager import names as n
from matrix.st_response_model.feature_engineering.utils import filter_before_normalization
from matrix.st_response_model.model_settings import model_settings
from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass(frozen=True)
class TransformationFeature:
    """Object to handle transformation / inverse-transformation of a single feature"""

    steps: List
    parameters: Dict

    @property
    def normalize(self):
        return [(step, self.parameters.get(step, [])) for step in self.steps]

    @property
    def denormalize(self):
        return [(step, self.parameters.get(step, [])) for step in self.steps[::-1]]


@dataclass(frozen=True)
class TransformationParams:
    """Object centralizing information to transform all features"""

    transformation_log: Dict  # constants used to normalized features

    def get_feature_params(self, feature_name: str) -> TransformationFeature:
        dictionary = model_settings.get_normalization_dict()
        return TransformationFeature(
            steps=list(dictionary[feature_name]),
            parameters={k[1]: v for k, v in self.transformation_log.items() if k[0] == feature_name},
        )


def normalize_feature(
    feature_df: pd.DataFrame,
    normalization_params_feature: TransformationFeature,
    column_feature: str = n.F_FEATURE_VALUE,
) -> pd.Series:
    """
    Scaling factor is brand and / or feature specific
    This function normalizes / transforms a single feature.

    Args:
        - feature_df: data frame with the feature value and the corresponding brand
        - feature_raw: name of the column with the raw / de-normalized feature values
    """
    normalized_feature = feature_df[column_feature].copy()
    if model_settings.REGIONAL_MODEL:
        model_granularity = (
            feature_df[[n.F_BRAND, n.F_REGION_GROUP]].set_index([n.F_BRAND, n.F_REGION_GROUP]).index
        )
    else:
        model_granularity = feature_df[n.F_BRAND]

    for step, params in normalization_params_feature.normalize:

        if step == "log":
            normalized_feature = np.log(normalized_feature + 1)

        elif step == "minus_log":
            normalized_feature = -np.log(1 - normalized_feature)

        elif step == "log_epsilon":
            normalized_feature = np.log(normalized_feature + 1e-6)

        elif step in ["max", "div_max_minus_mean", "std"]:
            scaling_factor = pd.Series(model_granularity.map(params), index=feature_df.index)
            normalized_feature = normalized_feature / scaling_factor

        elif step in ["minus_mean", "minus_min"]:
            scaling_factor = pd.Series(model_granularity.map(params), index=feature_df.index)
            normalized_feature = normalized_feature - scaling_factor

        elif step in ["max_across_brands", "custom_normalization"]:
            scaling_factor = params
            normalized_feature = normalized_feature / scaling_factor

        elif step == "max_across_brands_and_region":
            scaling_factor = pd.Series(model_granularity.map(params), index=feature_df.index)
            normalized_feature = normalized_feature / scaling_factor

        elif step == "custom_normalization_by_region":
            scaling_factor = feature_df[n.F_REGION_GROUP].map(params)
            normalized_feature = normalized_feature / scaling_factor

        elif step == "max_across_brands_by_region":
            scaling_factor = feature_df[n.F_REGION_GROUP].map(params)
            normalized_feature = normalized_feature / scaling_factor

        else:
            raise NotImplementedError(f"Unknown normalization step ... {step}")

    return normalized_feature


def denormalize_feature(
    feature_df: pd.DataFrame,
    normalization_params_feature: TransformationFeature,
    column_feature: str = n.F_FEATURE_VALUE,
) -> pd.Series:
    """
    De-normalize / inverse data transformation from pre-processing
    """
    denormalized_feature = feature_df[column_feature].copy()
    if model_settings.REGIONAL_MODEL:
        model_granularity = (
            feature_df[[n.F_BRAND, n.F_REGION_GROUP]].set_index([n.F_BRAND, n.F_REGION_GROUP]).index
        )
    else:
        model_granularity = feature_df[n.F_BRAND]

    for step, params in normalization_params_feature.denormalize:

        if step == "log":
            denormalized_feature = np.exp(denormalized_feature) - 1

        elif step == "minus_log":
            denormalized_feature = 1 - np.exp(-denormalized_feature)

        elif step == "log_epsilon":
            denormalized_feature = np.exp(denormalized_feature) - 1e-6

        elif step in ["max_across_brands", "custom_normalization", "max_across_brands_and_region"]:
            scaling_factor = params
            denormalized_feature = denormalized_feature * scaling_factor

        elif step in ["max", "std", "div_max_minus_mean"]:
            scaling_factor = pd.Series(model_granularity.map(params), index=feature_df.index)
            denormalized_feature = denormalized_feature * scaling_factor

        elif step in ["minus_mean", "minus_min"]:
            scaling_factor = pd.Series(model_granularity.map(params), index=feature_df.index)
            denormalized_feature = denormalized_feature + scaling_factor

        elif step in ["max_across_brands_by_region"]:
            scaling_factor = feature_df[n.F_REGION_GROUP].map(params)
            denormalized_feature = denormalized_feature * scaling_factor

        elif step in ["custom_normalization_by_region"]:
            scaling_factor = feature_df[n.F_REGION_GROUP].map(params).astype(float)
            denormalized_feature = denormalized_feature * scaling_factor

        else:
            raise NotImplementedError("Unknown normalization step ... {step}")

    return denormalized_feature


def _get_touchpoints_affected_by_filtering(channel: str) -> List[str]:
    """
    Function that records the touchpoints that will have to be filtered during normalization
    by the additional column keep data. They correspond to touchpoint specific to the channel
    not transformed with adstocks
    """
    channels = [item["channel"] for item in model_settings.YEAR_WEEKS_TO_BE_PUT_AS_NAN]
    if channel in channels:
        channel_touchpoints = dict(model_settings.TOUCHPOINT_BY_CHANNEL)[channel]
        touchpoints_to_reindex = [
            touchpoint
            for touchpoint in channel_touchpoints
            if touchpoint not in model_settings.STAN_IDX_ADSTOCK
        ]
    else:
        touchpoints_to_reindex = []

    return touchpoints_to_reindex


def normalize_raw_data(
    transformed_features: pd.DataFrame,
    normalization_steps_dict: Dict,
    normalization_custom_dict: Dict,
    channel: str,
) -> Tuple[pd.DataFrame, TransformationParams]:
    """
    Normalize pre-processed features / signals using the strategies specified by developers

    Args:
        - raw_features_df: Features table
        - normalization_steps: ordered sequence of transformations to apply for each feature
        - normalization_custom: custom normalization values for specific touchpoints (e.g.
        saturation of media touchpoints).
    """
    # Reset index
    normalized_features = transformed_features.copy()
    transformation_log = {}
    groupby_keys = [n.F_BRAND]
    if model_settings.REGIONAL_MODEL:
        groupby_keys.append(n.F_REGION_GROUP)
    touchpoints_to_reindex = _get_touchpoints_affected_by_filtering(channel=channel)

    for feature in set(normalization_steps_dict.keys()).intersection(set(normalized_features.columns)):

        normalized_features, normalized_features_out_of_scope = filter_before_normalization(
            normalized_features_df=normalized_features, feature_to_normalize=feature
        )
        # This for loop is iterating on list of touchpoints that are supposed to be disjoints
        # so the object drop period mask ony set once and not overwritten
        for touchpoints in touchpoints_to_reindex:
            if feature in touchpoints:
                drop_period_mask = normalized_features[n.F_KEEP_DATA]
                break
        else:
            drop_period_mask = pd.Series(data=True, index=normalized_features.index)

        for step in normalization_steps_dict[feature]:

            if step == "log":
                normalized_features[feature] = np.log(normalized_features[feature] + 1)

            elif step == "minus_log":
                normalized_features[feature] = -np.log(1 - normalized_features[feature])

            elif step == "log_epsilon":
                normalized_features[feature] = np.log(normalized_features[feature] + 1e-6)

            elif step == "max":
                # Assumption: When normalizing, whenever there is no spend on a brand (max = 0),
                # then transformation_log forces it to be equal at 1
                group = normalized_features[drop_period_mask].groupby(groupby_keys)[feature]
                coef_to_apply_per_brand_and_region = group.max().replace(0, 1).to_dict()
                transformation_log[(feature, step)] = coef_to_apply_per_brand_and_region
                series = normalized_features[groupby_keys].set_index(groupby_keys).index
                scaling_factor = pd.Series(
                    series.map(coef_to_apply_per_brand_and_region), index=normalized_features.index
                )
                normalized_features[feature] = normalized_features[feature] / scaling_factor

            elif step == "max_across_brands_by_region":
                group = normalized_features[drop_period_mask].groupby(n.F_REGION_GROUP)[feature]
                coef_to_apply_per_region = group.max().replace(0, 1).to_dict()
                transformation_log[(feature, step)] = coef_to_apply_per_region
                scaling_factor = normalized_features[n.F_REGION_GROUP].map(coef_to_apply_per_region)
                normalized_features[feature] = normalized_features[feature] / scaling_factor

            elif step in ["max_across_brands", "median_across_brands", "max_across_brands_and_region"]:
                if step == "median_across_brands":
                    coef_to_apply = normalized_features.loc[
                        drop_period_mask & (normalized_features[feature] > 0), feature
                    ].median()
                else:
                    coef_to_apply = normalized_features.loc[drop_period_mask, feature].max()
                if coef_to_apply == 0:
                    coef_to_apply = 1  # If no value, divide 0 by 1
                transformation_log[(feature, step)] = coef_to_apply
                normalized_features[feature] = normalized_features[feature] / coef_to_apply

            elif step == "div_max_minus_mean":
                group = normalized_features[drop_period_mask].groupby(groupby_keys)[feature]
                mean = group.mean().replace(0, 1).to_dict()
                max = group.max().replace(0, 1).to_dict()
                coef_to_apply_per_brand_and_region = {
                    brand: max[brand] - mean[brand] for brand in mean.keys()
                }
                transformation_log[(feature, step)] = coef_to_apply_per_brand_and_region
                scaling_factor = normalized_features[n.F_BRAND].map(coef_to_apply_per_brand_and_region)
                normalized_features[feature] = normalized_features[feature] / scaling_factor

            elif step == "minus_mean":
                group = normalized_features[drop_period_mask].groupby(groupby_keys)[feature]
                coef_to_apply_per_brand_and_region = group.mean().to_dict()
                transformation_log[(feature, step)] = coef_to_apply_per_brand_and_region
                normalized_features.loc[drop_period_mask, feature] = group.transform(lambda x: x - x.mean())

            elif step == "std":
                # Assumption: When normalizing, if no spend for a given category (max = 0),
                # then transformation_log put equal at 1
                group = normalized_features[drop_period_mask].groupby(groupby_keys)[feature]
                coef_to_apply_per_brand_and_region = group.std().replace(0, 1).to_dict()
                transformation_log[(feature, "std")] = coef_to_apply_per_brand_and_region
                normalized_features.loc[drop_period_mask, feature] = group.transform(
                    lambda x: x / x.std() if x.std() != 0 else x
                )

            elif step == "minus_min":  # Subtract minimum value for the brand
                group = normalized_features[drop_period_mask].groupby(groupby_keys)[feature]
                coef_to_apply_per_brand_and_region = group.min().to_dict()
                transformation_log[(feature, step)] = coef_to_apply_per_brand_and_region
                normalized_features.loc[drop_period_mask, feature] = group.transform(lambda x: x - x.min())

            elif step == "custom_normalization":
                try:
                    coef_to_apply = normalization_custom_dict[feature]
                except KeyError as err:
                    logging.critical(f"No normalization parameter specified for feature {feature}")
                    raise err
                transformation_log[(feature, step)] = coef_to_apply
                normalized_features[feature] = normalized_features[feature] / coef_to_apply

            elif step == "custom_normalization_by_region":
                try:
                    coefficients = normalization_custom_dict[feature]
                except KeyError as err:
                    logging.critical(f"No normalization parameter specified for feature {feature}")
                    raise err
                region_share_pop = transformed_features[
                    [n.F_REGION_GROUP, n.F_SHARE_POPULATION]
                ].drop_duplicates()
                coef_to_apply_per_region = dict(
                    zip(
                        region_share_pop[n.F_REGION_GROUP],
                        region_share_pop[n.F_SHARE_POPULATION] * coefficients,
                    )
                )
                transformation_log[(feature, step)] = coef_to_apply_per_region
                scaling_factor = normalized_features[n.F_REGION_GROUP].map(coef_to_apply_per_region)
                normalized_features[feature] = normalized_features[feature] / scaling_factor
            else:
                raise NotImplementedError(f"Step {step} not implemented")

        normalized_features = pd.concat(
            [normalized_features, normalized_features_out_of_scope], axis=0
        ).sort_values(by=[n.F_BRAND, n.F_YEAR_WEEK])

    transformation_params = TransformationParams(transformation_log)
    return normalized_features, transformation_params
