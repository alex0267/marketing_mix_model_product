import yaml
import pandas as pd
import Data_Preparation.mainDataPreparation


def test_data_preparation(): 

    # get config to give as parameter to the run function
    outputConfig = yaml.safe_load(open('../config/BaseConfig.yaml', 'r'))
    
    # df obtained
    df = Data_Preparation.mainDataPreparation.run(outputConfig)

    files_names = ["spending_df.csv", "seasonality_df.csv", "price_df.csv", "feature_df.csv", "control_df.csv", "targetRaw_df.csv", "indexColumns_df.csv"]

    # we need to read into output csv that corresponds to what the data should be in output given our entries
    # make assert for each df between what is obtained above and what we should have got
    for dataframe, file in zip(df, files_names):
        reference = pd.DataFrame(pd.read_csv("../Data_Preparation/EXPECTED_OUTPUT/"+file).round(4).astype(str))
        dataframe = pd.DataFrame(dataframe.round(4).astype(str))
        assert dataframe.equals(reference)
