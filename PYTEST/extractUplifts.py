
def extractUplifts(spendings, prediction, subset, touchpoint, scope):
    '''extracting all dataframes for testing'''


    #extract one for each touchpoint to test touchpoint accuracy

    spendings[(subset,touchpoint,1.0)].to_csv(f'PYTEST/COMPARE_FRAMES/UPLIFT_COMPARISON_{scope}/spendings_COMPARE_{subset}_{touchpoint}.csv')
    pred = prediction[(subset,touchpoint,1.0)] - prediction[(subset,touchpoint,0.0)]
    pred.to_csv(f'PYTEST/COMPARE_FRAMES/UPLIFT_COMPARISON_{scope}/prediction_COMPARE_{subset}_{touchpoint}.csv')


    #extract one for two lift levels (0.6 & 1.6 times the original spendings)
    #to test for uplift capability

    spendings[(subset,touchpoint,0.6)].to_csv(f'PYTEST/COMPARE_FRAMES/UPLIFT_COMPARISON_{scope}/spendings_COMPARE_LIFTS_{subset}_{touchpoint}_lift_06.csv')
    pred = prediction[(subset,touchpoint,0.6)] - prediction[(subset,touchpoint,0.0)]
                    
    pred.to_csv(f'PYTEST/COMPARE_FRAMES/UPLIFT_COMPARISON_{scope}/prediction_COMPARE_LIFTS_{subset}_{touchpoint}_lift_06.csv')

    spendings[(subset,touchpoint,1.6)].to_csv(f'PYTEST/COMPARE_FRAMES/UPLIFT_COMPARISON_{scope}/spendings_COMPARE_LIFTS_{subset}_{touchpoint}_lift_16.csv')
    pred = prediction[(subset,touchpoint,1.6)] - prediction[(subset,touchpoint,0.0)]
    pred.to_csv(f'PYTEST/COMPARE_FRAMES/UPLIFT_COMPARISON_{scope}/prediction_COMPARE_LIFTS_{subset}_{touchpoint}_lift_16.csv')
    
    return 0

def extractUpliftsSummary(spendings, prediction, subset, touchpoint):
    '''this uplift extraction is more targeted to reduce the amount of data to analyze while allowing to 
    test the entire scope of functionality'''

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
