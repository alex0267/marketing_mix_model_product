# Marketing_mix_model
First Prototype of a bayesian marketing mix model via STAN

## Structure
    .
    ├── Business_Output         # Calculates interpretable metrics in form of spending response curves per brand & touchpoint
    ├── config                  # yaml config files
    ├── Data                    # Collection of data sources in the form of .csv-files
    ├── Data_Preparation        # Contains the data preparation pipeline, feature engineering and normalization
    │   ├── main_Data_Preparation.py
    │   ├── seasonality.py
    │   ├── promotion.py
    │   ├── normalization.py
    │   ├── datetime_module.py
    │   └── names.py
    └── Response_Model          # Executes the Bayesian Marketing Mix Model

## Implementation

### Data_Preparation
Contains the data preparation pipeline.
Processes data tables for feature creation and feature normalization. 

**main_preprocessing.py**  
Collects and executes all pre-processing modules:
- Event & seasonality features
- Competitor price feature - TO BE IMPLEMENTED
- Promotion feature - TO BE IMPLEMENTED
- Off-trade visibility feature - TO BE IMPLEMENTED

**seasonality.py**<br/>
Calculates event & seasonality features that can be used as a lookup table.<br/> 
- Input: YEAR_WEEK - YYYYCW indices in scope
- FUNCTIONS: Calculation of seasonality & event features based on YEAR_WEEK
- Output: Table of features by YEAR_WEEK - https://drive.google.com/drive/folders/1ERElXW9XiUjhq_o5Jiqm9a_fz-s0mSwm

**datetime_module.py**<br/>
Supports datetime specific calculations in seasonality.py

**names.py** - CURRENTLY NOT IN USE<br/>
Module to standardize the column names in the code


### Response_Model : MMM Model
TO BE DEFINED

### Business_Output : After-processing
TO BE DEFINED

