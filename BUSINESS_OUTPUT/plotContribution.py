import pylab as plt
import numpy as np
import pandas as pd


def plotYearlyContribution(volumeContribution):

    return 0


def plotWeeklyContribution(volumeContribution,name):
    #define X-axis
    len_X = len(volumeContribution.responseModel.index_df['YEAR_WEEK'])

    #define the contribution factors in the right order
    contributors = pd.DataFrame()
    for item in volumeContribution.outputConfig['CONTRIBUTORS']:
        contributors = pd.concat([contributors,volumeContribution.deltaToZeroDict['ALL'][item]], axis=1)
        
    
    contributors = contributors.T


    X = np.arange(0, len_X, 1) 

    plt.plot()
    plt.stackplot(X, contributors, baseline="zero", labels=contributors.index)
    lgd = plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    
    plt.plot(volumeContribution.responseModel.filteredFeature_df['TARGET_VOL_SO'], color='black')
    plt.title('Volume Contribution by contributor')
    plt.axis('tight')
    plt.savefig(f'PLOTS/Contribution_Stacked_Area_Plot_{name}.png', bbox_extra_artists=(lgd,), bbox_inches='tight')
    plt.clf()


def plotContribution(volumeContribution, name):
    plotWeeklyContribution(volumeContribution,name)
    plotYearlyContribution(volumeContribution)