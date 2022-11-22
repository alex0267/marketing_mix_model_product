import HELPER_FUNCTIONS.transformations
import sklearn.metrics



def calculateError(responseModel, volumeContribution):
    r2_collection=[]
    for brand in responseModel.baseConfig['BRANDS']:
        filteredFeature_df = responseModel.filteredFeature_df[responseModel.filteredFeature_df['BRAND']==brand]
        #take prediction as weekly prediction without error correction
        prediction = volumeContribution.deltaToZeroDict[(brand,'ALL')]['total_predict']
        target = filteredFeature_df['TARGET_VOL_SO']

        print('MAPE')
        print(HELPER_FUNCTIONS.transformations.mean_absolute_percentage_error(prediction, target))

        print('R2')
        r2 = sklearn.metrics.r2_score(target, prediction)
        r2_collection.append(r2)
        

    return r2_collection
