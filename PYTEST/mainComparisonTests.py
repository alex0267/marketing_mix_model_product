import pandas as pd
import numpy as np
import json
import os
import PYTEST.upliftComparison



def compareEntryData():
    directory = 'PYTEST/COMPARE_FRAMES/ENTRY_DATA_COMPARISON_MASTER'
    directory_2 = 'PYTEST/COMPARE_FRAMES/ENTRY_DATA_COMPARISON_TEST'

    for file in os.listdir(directory):
        file_1 = f'PYTEST/COMPARE_FRAMES/ENTRY_DATA_COMPARISON_MASTER/{str(file)}'
        file_2 = f'PYTEST/COMPARE_FRAMES/ENTRY_DATA_COMPARISON_TEST/{str(file)}'


        if str(file_1)[-4:] == 'json':
            with open(file_1) as json_file:
                file_1 = json.load(json_file)

            with open(file_2) as json_file:
                file_2 = json.load(json_file)

            if (file_1 != file_2):
                print(f'{str(file)} not equal')
                print(file_1)
                print(file_2)
            else:
                print(f'{str(file)} equal')
            
        elif str(file_1)[-4:] == '.csv':
            file_1 = pd.read_csv(file_1)
            file_2 = pd.read_csv(file_2)


            if (file_1.round().equals(file_2.round())):
                print(f'{str(file)} not equal')
                print(file_1)
                print(file_2)
            else:
                print(f'{str(file)} equal')


    

def runComparisonTests():

    PYTEST.compareEntryData()
    PYTEST.upliftComparison.compareUplifts()
    '''
    The function is providing the pipeline for comparisonTests to assure that the dataframes do not change after commit.
    '''
    return 0
