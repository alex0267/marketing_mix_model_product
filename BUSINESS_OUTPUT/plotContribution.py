import pylab as plt
import numpy as np
import pandas as pd
import os


def plotYearlyContribution(volumeContribution,brand):

    return 0


def plotWeeklyContribution(volumeContribution,filteredFeature_df,brand,name):
    #define X-axis
    len_X = len(filteredFeature_df['YEAR_WEEK'])
    print(brand)
    print('len X')
    print(len_X)

    #define the contribution factors in the right order
    contributors = pd.DataFrame()
    for item in volumeContribution.outputConfig['CONTRIBUTORS']:
        contributors = pd.concat([contributors,volumeContribution.deltaToZeroDict[(brand,'ALL')][item]], axis=1)
        
    contributors = contributors.T
    print(contributors.sum())

    X = np.arange(0, len_X, 1) 

    plt.plot()
    plt.stackplot(X, contributors, baseline="zero", labels=contributors.index)
    lgd = plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    
    plt.plot(filteredFeature_df['TARGET_VOL_SO'], color='black')
    plt.title('Volume Contribution by contributor')
    plt.axis('tight')
    plt.savefig(f'PLOTS/{name}/Contribution_Stacked_Area_Plot_{brand}.png', bbox_extra_artists=(lgd,), bbox_inches='tight')
    plt.clf()


def plotContribution(volumeContribution, configurations, name):
    os.mkdir(f'PLOTS/{name}')
    for brand in configurations['BRANDS']:
        filteredFeature_df = volumeContribution.responseModel.filteredFeature_df[volumeContribution.responseModel.filteredFeature_df['BRAND']==brand].reset_index()

        plotWeeklyContribution(volumeContribution,filteredFeature_df,brand,name)
        plotYearlyContribution(volumeContribution,brand)