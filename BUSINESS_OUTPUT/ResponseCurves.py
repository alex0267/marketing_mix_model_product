import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import HELPER_FUNCTIONS.getIndex
import os

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

    def __init__(self, simulatedSpendings, simulatedSales, responseModel,outputConfig, price_df,name):
        
        #initial response Model

        self.simulatedSpendings = simulatedSpendings
        self.simulatedSales = simulatedSales

        self.responseModel = responseModel
        self.outputConfig = outputConfig
        self.price_df = price_df
        self.name = name

        #Attributes
        self.spendings = {}
        self.deltaSales = {}

        #execute pipeline
        self.run()


        
    def createResponseCurves(self, brand,subset):

        for touchpoint in self.outputConfig['RESPONSE_CURVE_TARGETS']:
            plt.plot(self.spendings[(brand,subset, touchpoint)].values(),self.deltaSales[(brand,subset, touchpoint)].values(), label=touchpoint)
            plt.legend()

        
        plt.savefig(f'BUSINESS_OUTPUT/RESPONSE_CURVE_PLOTS/{self.name}/responseCurve_{brand}_{subset}.png')
        plt.clf()
        return 0

    
    def run(self):

        analyzeRC_df= []

        #we create a path to gather the outputs per run
        path = f'BUSINESS_OUTPUT/RESPONSE_CURVE_PLOTS/{self.name}'
        if not os.path.isdir(path):
            os.mkdir(path)

        for brand in self.responseModel.configurations['BRANDS']:
            filteredFeature_df = self.responseModel.filteredFeature_df[self.responseModel.filteredFeature_df['BRAND']==brand].reset_index()
            price_df = self.price_df[self.price_df['BRAND']==brand]['NET_PRICE'].reset_index()
            

            #Execute calculation for different scopes (years individ. & all together)
            for subset in self.outputConfig['RESPONSE_CURVE_PERIODS']:
                #Simulate sales for each touchpoint and lift level
                
                
                #get indexes of data for respective time frame
                ind, cont = HELPER_FUNCTIONS.getIndex.getIndex(indexColumns = filteredFeature_df,scope='YEAR' , subset=subset)
                
                
                #required to skip years that are not in scope (for kFold split of R2 backtest)
                if cont == True: continue
                adstock_length = self.responseModel.responseModelConfig['MAX_LAG']
                index = filteredFeature_df.index

                #define extended_length as the max index + the maximum adstock length to increase size of frame in scope
                '''
                extended_index = ind[-1]+1 + adstock_length
                
                #if the end of the list is not reached -> extend list elements to include max length of adstock
                if (extended_index in index):
                    rangeList = [*range(ind[-1]+1, extended_index,1)]
                    ind.extend(rangeList)
                    
                '''
                for touchpoint in self.responseModel.configurations['TOUCHPOINTS']:
                    spendings = {}
                    deltaSales = {}

                    #Still need to add the adstock length
                   
                    salesNoSpends = self.simulatedSales[(brand, subset, touchpoint, 0.0)].iloc[ind]

                    for lift in self.outputConfig['SPEND_UPLIFT_TO_TEST']:
                    
                        #get the spendings for the touchpoint & subset in scope
                        spends = self.simulatedSpendings[(brand,subset, touchpoint, lift)][touchpoint].iloc[ind]
                        spendings[lift] = sum(spends)

                        #Still need to add the adstock length
                        vol = self.simulatedSales[(brand,subset, touchpoint, lift)].iloc[ind] - salesNoSpends
                        
                        prices = price_df['NET_PRICE'].iloc[ind]

                        sales = vol*prices

                        deltaSales[lift] = sum(sales)

                    self.spendings[(brand,subset, touchpoint)]= spendings
                    self.deltaSales[(brand,subset, touchpoint)] = deltaSales

                    for (k,v), (k2,v2) in zip(spendings.items(), deltaSales.items()):
                        analyzeRC_df.append([brand,subset,touchpoint,v,v2])
                    

                self.createResponseCurves(brand,subset)

        analyzeRC_df = pd.DataFrame(analyzeRC_df)

        analyzeRC_df.to_excel('analyseRC_df.xlsx')

                        

