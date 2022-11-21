import stan
import pandas as pd
import numpy as np
import HELPER_FUNCTIONS.normalization
import HELPER_FUNCTIONS.summarize
import PYTEST.extractEntryData
import PYTEST.mainComparisonTests
import json

#class that contains the input and output data of a specific response model with respective model settings
#Also contains the functions to estimate and extract parameters
class ResponseModel:

    def __init__(self,configurations, responseModelConfig, feature_df, filteredFeature_df, normalizedFeature_df, normalizedFilteredFeature_df, index_df, stanCode):
        #define configurations
        self.configurations = configurations
        self.responseModelConfig = responseModelConfig

        #data
        self.feature_df = feature_df
        self.filteredFeature_df = filteredFeature_df
        self.normalizedFeature_df = normalizedFeature_df
        self.normalizedFilteredFeature_df = normalizedFilteredFeature_df
        self.index_df = index_df

        #define data normalized
        self.spendings_df_normalized, self.touchpointNorms = HELPER_FUNCTIONS.normalization.normalize_feature(filteredFeature_df[configurations['TOUCHPOINTS']],filteredFeature_df[configurations['TOUCHPOINTS']], self.responseModelConfig['NORMALIZATION_STEPS_TOUCHPOINTS'])
                
        #easy access variables
        self.num_touchpoints = None

        #contains the output estimated variables
        self.extractFrame = None  #contains the raw bayesian estimations
        self.parameters = None  #contains the summarized estimated parameters

        #Define stan dictionary used for the stan model
        self.stanDict = None
        self.createDict()

        #Define stan code
        self.stanCode = stanCode
        
    

    def createArrayPerBrand(self, column):
        '''
        The stan model requires a slightly different table setup.
        Since columns cannot be named in stan, indexing becomes quite difficult to oversee.
        This approach creates arrays of size [N, BRANDS] for each touchpoint to keep indexing simple.
        '''

        array = []
        for brand in self.configurations['BRANDS']:
            feature_df = self.normalizedFilteredFeature_df.copy()
            element = feature_df[feature_df['BRAND']== brand][column]

            #in case there are no associated spendings for a specific touchpoint, add a 0 column (we need complete dataframes for stan)
            if(len(element) == 0):
                element =  [0 for x in range(len(feature_df[self.configurations['TOUCHPOINTS']]))]

            array.append(element)

        #add trailing 0's at touchpoints to account for adstock calculation overlap (calculating first weeks needs 0 weeks before first week)
        array = np.array(array)
        if(column in (self.configurations['TOUCHPOINTS'])):
            array = np.concatenate((np.zeros((len(self.configurations['BRANDS']),self.responseModelConfig['MAX_LAG']-1)),array),axis=1)
            
        
        return array


    def createDict(self):

        '''
        create dictionary as input data for the stan model
        '''
        self.num_touchpoints = len(self.configurations['TOUCHPOINTS'])
        touchpointSpend_df = self.normalizedFilteredFeature_df[self.configurations['TOUCHPOINTS']]

        #the arrays have to be appended to account for the adstock overlap (last elements of series need to be adstocked as well)
        tom = self.createArrayPerBrand('tom')
        laura = self.createArrayPerBrand('laura')
        lisa = self.createArrayPerBrand('lisa')
        mary = self.createArrayPerBrand('mary')
        fiona = self.createArrayPerBrand('fiona')
        marc = self.createArrayPerBrand('marc')
        alex = self.createArrayPerBrand('alex')
        epros = self.createArrayPerBrand('epros')
        covid = self.createArrayPerBrand('covid')
        distribution = self.createArrayPerBrand('distribution')
        promotion = self.createArrayPerBrand('promotion')
        off_trade_visibility = self.createArrayPerBrand('off_trade_visibility')
        control = self.createArrayPerBrand(self.configurations['CONTROL_VARIABLES_BASE'])
        season = self.createArrayPerBrand(self.configurations['SEASONALITY_VARIABLES_BASE'])
        is_last_week = self.createArrayPerBrand('is_last_week')
        targetVar = self.createArrayPerBrand(self.configurations['TARGET'])
        

        self.stanDict = {
            'N': len(targetVar[0]),
            'B' : len(self.configurations['BRANDS']),
            'max_lag': self.responseModelConfig['MAX_LAG'], 
            'num_touchpoints': self.num_touchpoints,
            'tom': tom,
            'laura':laura,
            'lisa':lisa,
            'mary':mary,
            'fiona':fiona,
            'marc':marc,
            'alex':alex,
            'epros':epros,
            'distribution':distribution,
            'promotion':promotion,
            'off_trade_visibility':off_trade_visibility,
            'covid':covid,
            'touchpointNorms': self.touchpointNorms,
            'shape_shift': [self.responseModelConfig['SHAPE_SHIFT_PRIOR'][tp] for tp in self.configurations['TOUCHPOINTS']],
            'touchpointThresholds': [self.responseModelConfig['SHAPE_THRESHOLD_VALUE'][tp] for tp in self.configurations['TOUCHPOINTS']],
            'num_seasons': len(self.configurations['SEASONALITY_VARIABLES_BASE']),
            'seasonality': season[0],
            'is_last_week': is_last_week,
            'num_control': len(self.configurations['CONTROL_VARIABLES_BASE']),
            'control': control,
            'volume': targetVar
        }      
        
        
        dictTPSummary = pd.DataFrame()
        dictCTRLSummary = pd.DataFrame()
        for key in self.stanDict.keys():
            if key in self.configurations['TOUCHPOINTS'] :
                dictTPSummary[key] = self.stanDict[key][0]
            if key in self.configurations['CONTROL_VARIABLES_BASE'] :
                dictCTRLSummary[key] = self.stanDict[key][0]


        
        PYTEST.extractEntryData.extractEntryData(self.stanDict, 'stanDict', self.configurations['SET_MASTER'])
        

    def extractParameters(self, printOut=False):
        
        '''
        Extract parameters from trained model
        '''
        #pd.DataFrame(self.extractFrame.mean(axis=0)).to_csv('extractFrame.csv')
        self.parameters = {}

        for i,brand in enumerate(self.configurations['BRANDS'],start = 1):

            brandEstimationsDict = {}
            self.parameters[brand] = brandEstimationsDict

            brandEstimationsDict['intercept'] = self.extractFrame[f'intercept.{i}'].mean(axis=0)
            brandEstimationsDict['sigma'] = self.extractFrame[f'sigma.{i}'].mean(axis=0)

            #FOR NOW OK BUT NEED TO BE CHANGED WHEN SEASONALITY APPROACH IS CHANGED
            beta_seasonality=[]
            for s, season in enumerate(self.configurations['SEASONALITY_VARIABLES_BASE'],start = 1):
                beta_seasonality.append(self.extractFrame[f'beta_seasonality.{i}.{s}'].mean(axis=0))
            
            #we add a list as a dict object to facilitate beta extraction
            brandEstimationsDict[f'seasonality_beta'] = beta_seasonality

            beta_control=[]
            for c, control in enumerate(self.configurations['CONTROL_VARIABLES_BASE'],start = 1):
                beta_control.append(self.extractFrame[f'beta_{control}.{i}'].mean(axis=0))
            
            brandEstimationsDict[f'control_beta'] = beta_control

            for t, touchpoint in enumerate(self.configurations['TOUCHPOINTS'],start = 1):

                brandEstimationsDict[f'{touchpoint}_peak']  = self.extractFrame[f'peak.{t}'].mean(axis=0)
                brandEstimationsDict[f'{touchpoint}_decay']  = self.extractFrame[f'decay.{t}'].mean(axis=0)
                #here we insert a non-trained parameter in the dict
                #It depends on the configurations but since it is the only parameter configured, this facilitates the structure
                #based on stanDict since to assure max_lag is equal to what is passed to the stan model
                brandEstimationsDict[f'{touchpoint}_max_lag']  = self.stanDict['max_lag']
                brandEstimationsDict[f'{touchpoint}_beta']  = self.extractFrame[f'beta_{touchpoint}.{i}'].mean(axis=0)
                brandEstimationsDict[f'{touchpoint}_shape'] = self.extractFrame[f'shape.{t}'].mean(axis=0)
                brandEstimationsDict[f'{touchpoint}_scale'] = self.extractFrame[f'scale.{t}'].mean(axis=0)

        return 0


    def transform(self, df, outputName):
        
        # tran_df = pd.DataFrame(df.iloc[:,:70].mean())
        tran_df = pd.DataFrame(df.mean())
        tran_df.to_excel(f'OUTPUT/{outputName}/estimatedParametersMean.xlsx')
  

        return tran_df

    def runModel(self, name,outputName, load=True):
        '''
        Run stan model with created dictionary and save results
        '''

        if(load==False):
            posterior = stan.build(self.stanCode, data=self.stanDict)
            # fit = posterior.sample(num_chains=1, num_samples=1,num_warmup=0)
            fit = posterior.sample(num_chains=4, num_samples=1000)
            self.extractFrame = fit.to_frame()
            self.extractFrame.to_csv(f'MODEL_SAVINGS/extract{name}.csv')
            self.transform(self.extractFrame, outputName)

        else:
            self.extractFrame = pd.read_csv(f'MODEL_SAVINGS/extract{name}.csv')
            self.transform(self.extractFrame, outputName)
            
        
        return 0
