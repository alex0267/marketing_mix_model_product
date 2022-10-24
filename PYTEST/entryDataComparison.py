def compareStanDicts(stanDict):

    compareStanDict, compareSizeDict = extractDict(stanDict)
    with open("PYTEST/MASTER_FRAMES/masterStanDict.json","r") as f:
        masterStanDict = json.load(f)
    with open("PYTEST/MASTER_FRAMES/masterSizeDict.json","r") as f:
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
            
        if(compareStanDict['touchpointNorms'] != compareStanDict['touchpointNorms']):
            print('norms')

        

    if(compareSizeDict == masterSizeDict):
        print('dictionaries are the same in size')
    else:
        print('dictionaries are different in size')

    return 0