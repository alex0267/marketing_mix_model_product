""" Module to standardize the column names in the code """

# Dates
MONTHS_LIST = [
    "january",
    "february",
    "march",
    "april",
    "may",
    "june",
    "july",
    "august",
    "september",
    "october",
    "november",
    "december",
]
TIMESTAMP_PLACEHOLDER = "TS"
CHANNEL_PLACEHOLDER = "SUB"

F_YEAR_WEEK = "year_week"
F_YEAR_MONTH = "year_month"
F_YEAR_FISCAL = "fiscal_year"
F_YEAR_CALENDAR = "calendar_year"
F_YEAR = "year"
F_IS_FISCAL_YEAR = "is_fiscal_year"
F_IS_REFERENCE_OPTIMIZER = "is_reference_optimizer"
F_IS_BELOW_MIN_SPENDS_TO_SALES_RATIO = "filter_ratio_spend_sales"
F_PRICE_PERIOD = "price_period"

# Key columns
F_PRICE_BAND = "price_band"
F_REF_PRICE = "reference_price"
F_SCOPE = "scope"
F_DESCRIPTIVE_STATISTICS = "descriptive_statistics"

DESCRIPTIVE_STAT_TO_SUFFIX_MAP = {"Q10": "_p10", "mean": "", "Q90": "_p90"}

# Product hierarchy
F_SKU = "sku"
F_SUB_BRAND = "sub_brand"
F_SUB_BRAND_COMPETITOR = "sub_brand_competitor"
F_BRAND = "brand"
F_BRAND_COMPETITOR = "brand_competitor"
F_BRAND_QUALITY_ID = "brand_quality_id"
F_BRAND_QUALITY = "brand_quality"  # BQ
F_BRAND_QUALITY_SIZE = "brand_quality_size"  # BQS = Product Group
F_CATEGORY = "category"
F_SKU_EAN = "ean"  # sell-out (case or bottle)

# Sell-in
F_SALES_NET = "net_sales"
F_SALES_CHANNEL = "sales_channel"  # on-trade, off-trade, e-com
F_SALES_CHANNEL_SUFFIX = "sales_channel_suffix"  # on, off, ec
F_COGS = "cogs"
F_VOLUME_IN_L = "volume_in_l"
F_PRICE_ASP_L_NET = "net_sales_asp_per_l"  # Computed based on Net Sales
F_CONTRIBUTION_MARGIN_PER_L = "contribution_margin_per_l"
F_DEPLETIONS = "depletions"

# Sell-out
F_ALCOHOL_PERC = "alcohol_percentage"
F_CHANNEL_DISTRIBUTION = "distribution_channel"  # on-trade, off-trade, e-com
F_CHANNEL_DISTRIBUTION_CODE = "distribution_code"
F_COMPANY = "company"  # Owner / manufacturer
F_SALES_SO = "sales_so"
F_SALES_SO_PROMO = "sales_so_promo"
F_SKU_SO = "sku_so"
F_SKU_SIZE = "sku_size"
F_VOLUME = "volume"
F_VOLUME_SO = "volume_so"  # in 9l c/s
F_VOLUME_SO_PROMO = "volume_so_promo"  # in 9l c/s
F_PRICE_ASP = "average_selling_price"
F_PRICE_DISCOUNT_FEATURE = "relative_gap_to_90th_price"
F_PRICE_ASP_L = "asp_per_l"
F_PRICE_ASP_L_PROMO = "asp_promo_per_l"
F_KEEP_DATA = "keep_data"

# Promo distribution feature + display
F_COMPETITORS_PRICE_ASP = "price_competitors"
F_COMPETITORS_PRICE_FEATURE = "discount_price_comp_to_pr"
F_DISTRIBUTION = "distribution"
F_DISTRIBUTION_PROMO = "distribution_promo"
F_DISTRIBUTION_DISPLAY = "distribution_display"
F_DISTRIBUTION_FEATURE = "distribution_feature"
F_DISTRIBUTION_FEATURE_DISPLAY = "distribution_feature_display"
F_OFF_TRADE_VISIBILITY = "off_trade_visibility"
F_PROMO_EPROS = "promo_epros"

# Scale factor sell out
F_SCALE_FACTOR = "scale_factor"

F_DISCOUNT_RATE = "discount_rate"
F_DISCOUNT = "discount_abs"


# Execution spend
F_EXECUTION = "execution"
F_GRP = "grp"
F_REACH = "reach"
F_IMPRESSIONS = "impressions"
F_CLICKS = "clicks"
F_SPEND_IN_BASELINE = "yearly_spend_in_baseline"
# ERP spend data
F_TOUCHPOINT = "touchpoint"
F_SPEND = "spend"  # euros
F_SPEND_TYPE = "spend_type"

# Spend promo data
F_SPEND_PROMO = "spend_promo"

# Response curve model
F_BRAND_INDEX = "b"  # brand index (in PyStan model)
F_TIME_INDEX = "t"  # time index (in PyStan model)
F_REGION_INDEX = "r"  # region index (in PyStan model)
F_UPLIFT = "uplift"
F_BRAND_IMPACT = "brand_impact"  # brand impact in volume (in opposition of brand spend)
F_SAMPLE_ID = "sample_id"

# Computed quantities
F_FEATURE_VALUE = "feature"
F_FEATURE_NORM = "feature_normalized"
F_FEATURE_REG = "feature_regression"  # co-variate in regression model
F_VOLUME_SO_PRED = "volume_so_f_denorm"  # denormalized forecast
F_VOLUME_SO_PRED_p10 = "volume_so_f_denorm_p10"
F_VOLUME_SO_PRED_p90 = "volume_so_f_denorm_p90"
F_FEATURE_BRAND_CONTRIBUTION = "feature_brand_contribution"
F_DELTA_TO_NULL_VOLUME = "delta_to_null_volume"
F_DELTA_TO_NULL_VOLUME_p10 = "delta_to_null_volume_p10"
F_DELTA_TO_NULL_VOLUME_p90 = "delta_to_null_volume_p90"
F_DELTA_TO_NULL_VOLUME_L = "delta_to_null_volume_in_l"
F_DELTA_TO_NULL_REVENUES_L = "delta_to_null_revenues_in_l"
F_DELTA_TO_NULL_REVENUES_L_p10 = "delta_to_null_revenues_in_l_p10"
F_DELTA_TO_NULL_REVENUES_L_p90 = "delta_to_null_revenues_in_l_p90"
F_LAMBDA_ADSTOCK = "lambda_adstock"

# Metrics
F_R_SQUARE = "r_square"
F_MEAN_ABSOLUTE_ERROR = "mean_absolute_error"
F_MAPE = "mean_absolute_percentage_error"

# Accounting metrics
F_SPEND_CONVERSION_RATE = "spend_conversion_rate"  # Conversion Marketing & Trade execution to spend
F_ROS = "ros"  # ROS = Return on Sell-out = (sell-out ASP * Volume uplift / Spend)
F_ROI = "roi"  # ROI = (CAAP / Spend)

# Recommendation engine outputs
F_METRIC_NAME = "metric"
F_TIME_HORIZON = "time_horizon"
F_IS_WITH_BASELINE = "is_with_baseline"
F_IS_NEW_TOUCHPOINT = "is_new_touchpoint"
F_MARKETING_TRADE_OVER_NET_SALES_RATIO = "marketing_trade_over_net_sales_ratio"
F_METRIC_VALUE = "value"
F_VALUE_FROM_ALLOC = "value_from_alloc"
F_VALUE_FROM_ROI_BOOST = "value_from_roi_boost"
F_VALUE_FROM_SPEND_BEYOND_RC = "value_from_spend_beyond_response_curves"
F_LAST_YEAR_VALUE_METRIC = "last_year_value"
F_LAST_YEAR_WITH_GROWTH_VALUE_METRIC = "last_year_with_growth_value"
F_LAST_YEAR_DELTA_VALUE_METRIC = "last_year_delta"
F_DELTA_FROM_GROWTH = "delta_from_growth"
F_DELTA_FROM_MATRIX = "delta_from_matrix"
F_LAST_YEAR_VARIATION_VALUE_METRIC = "last_year_variation"
F_VARIATION_FROM_GROWTH = "variation_from_growth"
F_VARIATION_FROM_MATRIX = "variation_from_matrix"
F_IS_IN_SCOPE_OPTI = "is_in_scope_optimizer"
F_HAS_FIXED_SPEND = "has_fixed_spend"

# Environment variables
E_GIT_COMMIT_HASH = "GIT_CURRENT_COMMIT"

# AzureML tags
TIMESTAMP_TAG = "run_timestamp"
RUN_HASH_TAG = "run_hash"
MODEL_HASH_TAG = "model_hash"
PRODUCTION_FLAG_TAG = "production_ready"
DATA_SOURCE_TAG = "data_source"
DATA_SCHEMA_VERSION_TAG = "schema_version"
COMMIT_HASH_TAG = "commit_hash"
YEAR_TAG = "year"
HALO_TAG = "halo_activated"
UNAVAILABLE = "unavailable"

# Geography
# Regions used for modeling
F_REGION_GROUP = "region_group"
F_NATIONAL_CHANNEL = "off_national"
F_REGION = "region"
F_NATIONAL = "national"

F_TURNOVER_MARKET_UNIT = "turnover_market_unit"
F_POPULATION = "population"
F_SHARE_POPULATION = "share_population"
F_GROCERY_STORE_TYPE = "grocery_store_type"
F_LIQUOR_STORE_TYPE = "liquor_store_type"
F_NABCA_STORE_TYPE = "nabca_store_type"

# Campaign
F_CAMPAIGN = "campaign"
F_CAMPAIGN_INDEX = "campaign_index"

# Covid measures
F_COUNTRY = "country"
F_OXFORD_INDEX = "oxford_index"
F_COMPOSITE_INDEX = "composite_index"
F_ZERO_SERIES = "zero_series"
F_BAR_RESTAURANT_CLOSURE = "bar_restaurant_closure"
F_LOCKDOWN_CURFEW = "lockdown_curfew"
F_NO_SOCIAL_GATHERING = "no_social_gathering"
F_MEASURE_INDEX = "measure_index"
F_MEASURE_INDEX_POSITIVE_DERIVATIVE = "measure_index_positive_derivative"
F_COVID_LEVEL_OF_RESTRICTION = "covid_level_of_restriction"
F_COVID_RESTRICTIONS_INCREASE = "covid_restrictions_increase"
F_COVID_ON_OUTLET_FACTOR = "covid_on_outlet_factor"
F_COVID_ALL_INCREASE_WEEKLY = "covid_all_increase_weekly"
F_CRACKDOWN_ON_IMPACT_OVERALL = "crackdown_on_impact_overall"
