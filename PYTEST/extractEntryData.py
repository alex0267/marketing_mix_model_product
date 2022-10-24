import json
import numpy as np
import pandas as pd


def extractDict(data,name,scope):
        newDict={}

        #json does not accept np or pd objects - must be converted
        for element in data:
            if isinstance(data[element],pd.DataFrame):
                newDict[element] = data[element].values.tolist()

            elif (type(data[element]).__module__)=='numpy':
                newDict[element] = data[element].tolist()

            else:
                newDict[element] = data[element]


        dictionary = json.dumps(newDict)
        f = open(f"PYTEST/COMPARE_FRAMES/ENTRY_DATA_COMPARISON_{scope}/{name}.json","w")
        f.write(dictionary)
        f.close()

        return 0



def extractEntryData(data, name, master):
    
    if master:
        scope = 'MASTER'
    else:
        scope ='TEST'

    if isinstance(data, dict):
        extractDict(data, name, scope)

    else:
        data.to_csv(f'PYTEST/COMPARE_FRAMES/ENTRY_DATA_COMPARISON_{scope}/{name}.csv')


