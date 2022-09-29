import pylab as plt
import numpy as np
import pandas as pd


def plotYearlyContribution(volumeContribution):
    return 0


def plotWeeklyContribution(volumeContribution):
    #define X-axis
    len_X = len(volumeContribution.responseModel.indexColumns['YEAR_WEEK'])

    #define the contribution factors in the right order
    contributors = pd.DataFrame()
    for item in volumeContribution.outputConfig['CONTRIBUTORS']:
        contributors = pd.concat([contributors,volumeContribution.deltaToZeroDict['ALL'][item]], axis=1)
    
    contributors = contributors.T

    X = np.arange(0, len_X, 1) 

    plt.plot()
    plt.stackplot(X, contributors, baseline="zero")
    plt.plot(volumeContribution.responseModel.target, color='black')
    plt.title('Volume Contribution by contributor')
    plt.axis('tight')
    plt.savefig('plots/Contribution_Stacked_Area_Plot.png')
    plt.clf()


def plotContribution(volumeContribution):
    plotWeeklyContribution(volumeContribution)
    plotYearlyContribution(volumeContribution)
