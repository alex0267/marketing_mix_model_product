# Marketing_mix_model
First Prototype of a bayesian marketing mix model via STAN

## Structure
    .
    ├── Data                    # Collection of data sources in the form of .csv-files
    ├── Preprocessing           # Contains the data preparation pipeline, feature engineering and normalization
    │   ├── main_preprocessing.py
    │   ├── seasonality.py
    │   ├── datetime_module.py
    │   └── names.py
    └── ...

## Implementation

### Pre-processing
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


### MMM Model
TO BE DEFINED

### After-processing
TO BE DEFINED

