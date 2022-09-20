import helper_functions.transformations
import sklearn.metrics



def calculateError(responseModel, volumeContribution):
    
    #take prediction as weekly prediction without error correction
    prediction = volumeContribution.deltaToZeroDict['ALL']['total_predict']
    target = responseModel.target

    print('MAPE')
    print(helper_functions.transformations.mean_absolute_percentage_error(prediction, target))

    print('R2')
    print(sklearn.metrics.r2_score(target, prediction))
