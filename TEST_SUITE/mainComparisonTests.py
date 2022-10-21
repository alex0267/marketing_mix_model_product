import pandas as pd
import numpy as np
import json



def compareUplifts(spendings, prediction, outputConfig, configurations):

    for subset in outputConfig['CHANGE_PERIODS']:
            #Simulate sales for each touchpoint and lift level
        for touchpoint in configurations['TOUCHPOINTS']:
            for lift in outputConfig['SPEND_UPLIFT_TO_TEST']:

                #spendings[(subset,touchpoint,lift)]
                




    return 0

def extractDict(stanDict):
        newDict={}
        sizeDict={}

        #json does not accept np or pd objects - must be converted
        for element in stanDict:
            if isinstance(stanDict[element],pd.DataFrame):
                newDict[element] = stanDict[element].values.tolist()
                sizeDict[element] = stanDict[element].shape
            elif (type(stanDict[element]).__module__)=='numpy':
                newDict[element] = stanDict[element].tolist()
                sizeDict[element] = stanDict[element].shape
            else:
                newDict[element] = stanDict[element]
                sizeDict[element] = stanDict[element]

        compareStanDict = json.dumps(newDict)
        f = open("TEST_SUITE/COMPARE_FRAMES/compareStanDict.json","w")
        f.write(compareStanDict)
        f.close()

        compareSizeDict = json.dumps(sizeDict)
        f = open("TEST_SUITE/COMPARE_FRAMES/compareSizeDict.json","w")
        f.write(compareSizeDict)
        f.close()

        return newDict, sizeDict

def compareStanDicts(stanDict):

    compareStanDict, compareSizeDict = extractDict(stanDict)
    with open("TEST_SUITE/MASTER_FRAMES/masterStanDict.json","r") as f:
        masterStanDict = json.load(f)
    with open("TEST_SUITE/MASTER_FRAMES/masterSizeDict.json","r") as f:
        masterSizeDict = json.load(f)

    if(compareStanDict == masterStanDict):
        print('dictionaries are the same')
        
    else:
        print('dictionaries are different')

        #Differency can come from names but might not come from the content -> compare content
        if(masterStanDict['touchpoint_spendings'] != compareStanDict['touchpointSpend_df']):
            print('spends different')

        if(masterStanDict['control'] != compareStanDict['control']):
            print('control different')

        if(masterStanDict['touchpoint_thresholds'] != compareStanDict['touchpointThresholds']):
            print('threshold different')
        
        if(masterStanDict['seasonality'] != compareStanDict['seasonality']):
            print('seasonality different')

        if(masterStanDict['y'] != compareStanDict['y']):
            print('y different')
        

    if(compareSizeDict == masterSizeDict):
        print('dictionaries are the same in size')
    else:
        print('dictionaries are different in size')

    return 0

def comparisonTests():
    '''
    The function is providing the pipeline for comparisonTests to assure that the dataframes do not change after commit.
    '''
    return 0