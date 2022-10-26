import pandas as pd

def setPredictData(dataSets, master):
    ''' Set the datasets of master or test depending on the scope'''

    if (master):
        scope = 'MASTER'
    else:
        scope = 'TEST'


    for data in dataSets:
        # data_flat = [val for sublist in data[0] for val in sublist]

    
        data[0].to_csv(f'PYTEST/COMPARE_FRAMES/UPLIFT_COMPARISON_{scope}/prediction_{data[1]}.csv',index=False)

def setSpendingsData(spends,master):
    if (master):
        scope = 'MASTER'
    else:
        scope = 'TEST'
    
    spends_datasets = [val for sublist in spends[0] for val in sublist]

    for i,spend in enumerate(spends_datasets):
        pd.DataFrame(spend).to_csv(f'PYTEST/COMPARE_FRAMES/UPLIFT_COMPARISON_{scope}/spendings_{i}.csv')


def extractSpendings(spendings, subset, touchpoint, lift):

    spend = spendings[(subset,touchpoint,lift)]

    return spend

def extractMeanPerPrediction(prediction, subset, touchpoint, lift):
    deltaWeeklyPred = prediction[(subset,touchpoint,lift)] - prediction[(subset,touchpoint,0.0)]
    deltaMeanPerPrediction = deltaWeeklyPred.mean()

    return deltaMeanPerPrediction

def extractMeanOfTotalPrediction(prediction, subset, touchpoint, lift):
    weeklyPred = prediction[(subset,touchpoint,lift)]
    meanPerPrediction = weeklyPred.mean()

    return meanPerPrediction

def extractWeeklyPrediction(prediction, subset, touchpoint, lift):
    weeklyPred = prediction[(subset,touchpoint,lift)] - prediction[(subset,touchpoint,0.0)]
    index = pd.Series([f'{touchpoint}_{subset}_{lift}_{x}' for x in range(len(weeklyPred))]).rename('index')
    weeklyPred_df = pd.concat([index,weeklyPred],axis=1)

    return weeklyPred_df

def extractUplifts(spendings, prediction, subset, touchpoint,lifts):
    '''extracting all dataframes for testing'''
    
    meansPerPrediction = pd.DataFrame()
    meanOfTotalPrediction = pd.DataFrame()
    weeklyPrediction = pd.DataFrame()
    spends = []

    for lift in lifts:
        new = pd.DataFrame([[f'{touchpoint}_{subset}_{lift}', extractMeanPerPrediction(prediction, subset, touchpoint, lift)]])
        meansPerPrediction = pd.concat([meansPerPrediction,new], axis = 0)

        new = pd.DataFrame([[f'{touchpoint}_{subset}_{lift}', extractMeanOfTotalPrediction(prediction, subset, touchpoint, lift)]])
        meanOfTotalPrediction = pd.concat([meanOfTotalPrediction,new], axis = 0)

        new = extractWeeklyPrediction(prediction, subset, touchpoint, lift)
        weeklyPrediction = pd.concat([weeklyPrediction,new], axis = 0)

        spends.append(extractSpendings(spendings, subset, touchpoint, lift))

    return meansPerPrediction, meanOfTotalPrediction, weeklyPrediction, spends


'''
def extractUpliftsSummary(spendings, prediction, subset, touchpoint):
    # his uplift extraction is more targeted to reduce the amount of data to analyze while allowing to 
    # test the entire scope of functionality

    #extract one for each year
    #which defines response cuves
    if(touchpoint=='alex'):
        spendings[(subset,touchpoint,1.0)].to_csv(f'PYTEST/COMPARE_FRAMES/2/spendings_COMPARE_YEARS_{subset}_{touchpoint}.csv')
        pred = prediction[(subset,touchpoint,1.0)] - prediction[(subset,touchpoint,0.0)]
        pred.to_csv(f'PYTEST/COMPARE_FRAMES/2/prediction_COMPARE_YEARS_{subset}_{touchpoint}.csv')

    #extract one for each touchpoint
    #basic touchpoint comparison showing volume contribution capability
    if(subset=='ALL'):
        spendings[(subset,touchpoint,1.0)].to_csv(f'PYTEST/COMPARE_FRAMES/2/spendings_COMPARE_TOUCHPOINTS_{subset}_{touchpoint}.csv')
        pred = prediction[(subset,touchpoint,1.0)] - prediction[(subset,touchpoint,0.0)]
        pred.to_csv(f'PYTEST/COMPARE_FRAMES/2/prediction_COMPARE_TOUCHPOINTS_{subset}_{touchpoint}.csv')


    #extract one for two lift levels (0.6 & 1.6 times the original spendings)
    #to test for the response curve generation
    if(subset=='ALL' and touchpoint=='alex'):
        spendings[(subset,touchpoint,0.6)].to_csv(f'PYTEST/COMPARE_FRAMES/2/spendings_COMPARE_LIFTS_{subset}_{touchpoint}_lift_06.csv')
        pred = prediction[(subset,touchpoint,0.6)] - prediction[(subset,touchpoint,0.0)]
                     
        pred.to_csv(f'PYTEST/COMPARE_FRAMES/2/prediction_COMPARE_LIFTS_{subset}_{touchpoint}_lift_06.csv')

        spendings[(subset,touchpoint,1.6)].to_csv(f'PYTEST/COMPARE_FRAMES/2/spendings_COMPARE_LIFTS_{subset}_{touchpoint}_lift_16.csv')
        pred = prediction[(subset,touchpoint,1.6)] - prediction[(subset,touchpoint,0.0)]
        pred.to_csv(f'PYTEST/COMPARE_FRAMES/2/prediction_COMPARE_LIFTS_{subset}_{touchpoint}_lift_16.csv')
    
    return 0
'''