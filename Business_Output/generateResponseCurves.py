import Business_Output.applyParameters
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import helper_functions.getIndex

class ResponseCurves:
    '''
    Generates the response curves based on the uplift simulations.

    Attributes:
    - spendings: Collection of the sum of all spendings for a specific (subset, touchpoint, lift)-combination
    - deltaSales: Collection of the sum of all deltaSales (sales uplift(u)- sales uplift(0)) for a specific subset, touchpoint, lift combination

    Parameters:
    - simulatedSpendings: Collection of changed spendings for a specific (subset, touchpoint, lift)-combination
    - simulatedSales: Collection of simulated sales for a specific (subset, touchpoint, lift)-combination
    '''

    def __init__(self, simulatedSpendings, simulatedSales, responseModel,outputConfig):
        
        #initial response Model

        self.simulatedSpendings = simulatedSpendings
        self.simulatedSales = simulatedSales

        self.responseModel = responseModel
        self.outputConfig = outputConfig

        #Attributes
        self.spendings = {}
        self.deltaSales = {}

        #execute pipeline
        self.run()


        
    def createResponseCurves(self, spendings, deltaSales, subset, touchpoint):

        plt.plot(spendings.values(),deltaSales.values())
        plt.savefig(f'Business_Output/responseCurvePlots/responseCurve_{subset}_{touchpoint}.png')
        plt.clf()
        return 0

    
    def run(self):

        #Execute calculation for different scopes (years individ. & all together)
        for subset in self.outputConfig['CHANGE_PERIODS']:
            #Simulate sales for each touchpoint and lift level

            #get indexes of data for respective time frame
            ind = helper_functions.getIndex.getIndex(indexColumns = self.responseModel.indexColumns,scope='YEAR' , subset=subset)
            adstock_length = self.responseModel.responseModelConfig['max_lag']
            index = self.responseModel.indexColumns.index

            #define extended_length as the max index + the maximum adstock length to increase size of frame in scope
            #print(ind[-1])
            extended_index = ind[-1]+1 + adstock_length
            #print(ind[-1]+1 + adstock_length)
            
            #if the end of the list is not reached -> extend list elements to include max length of adstock
            if (extended_index in index):
                rangeList = [*range(ind[-1]+1, extended_index,1)]
                ind.extend(rangeList)
                

            for touchpoint in self.responseModel.configurations['TOUCHPOINTS']:
                spendings = {}
                deltaSales = {}

                #Still need to add the adstock length
                salesNoSpends = self.simulatedSales[(subset, touchpoint, 0.0)].iloc[ind]

                for lift in self.outputConfig['SPEND_UPLIFT_TO_TEST']:
                
                    #get the spendings for the touchpoint & subset in scope
                    spends = self.simulatedSpendings[(subset, touchpoint, lift)][touchpoint].iloc[ind]
                    spendings[lift] = sum(spends)

                    #Still need to add the adstock length
                    sales = self.simulatedSales[(subset, touchpoint, lift)].iloc[ind] - salesNoSpends
                    deltaSales[lift] = sum(sales)

                self.spendings[(subset, touchpoint)]= spendings
                self.deltaSales[(subset, touchpoint)] = deltaSales

                self.createResponseCurves(spendings, deltaSales, subset, touchpoint)
                        
