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
        self.beta = []
        self.beta_seasonality = []
        self.beta_control = []

        #contains the output estimated variables
        self.extractFrame = None  #contains the raw bayesian estimations
        self.parameters = None  #contains the summarized estimated parameters
        self.controlParameters = None

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

        #add trailing 0's to account for adstock overlap
        array = np.array(array)
        if(column in (self.configurations['TOUCHPOINTS'])):
            array = np.concatenate((np.zeros((len(self.configurations['BRANDS']),self.responseModelConfig['MAX_LAG']-1)),array),axis=1)
            
        
        return array


    def createDict(self):

        '''
        create dictionary as input data for the stan model
        '''
        num_touchpoints = len(self.configurations['TOUCHPOINTS'])
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
        targetVar = self.createArrayPerBrand(self.configurations['TARGET'])

        # print(season.shape)
        

        self.stanDict = {
            'N': len(targetVar[0]),
            'B' : len(self.configurations['BRANDS']),
            'max_lag': self.responseModelConfig['MAX_LAG'], 
            'num_touchpoints': num_touchpoints,
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
            'touchpointThresholds': [self.responseModelConfig['SHAPE_THRESHOLD_VALUE'][tp] for tp in self.configurations['TOUCHPOINTS']],
            'num_seasons': len(self.configurations['SEASONALITY_VARIABLES_BASE']),
            'seasonality': season[0],
            'num_control': len(self.configurations['CONTROL_VARIABLES_BASE']),
            'control': control,
            'y': targetVar
        }
        print(targetVar)
        
        dictTPSummary = pd.DataFrame()
        dictCTRLSummary = pd.DataFrame()
        for key in self.stanDict.keys():
            if key in self.configurations['TOUCHPOINTS'] :
                dictTPSummary[key] = self.stanDict[key][0]
            if key in self.configurations['CONTROL_VARIABLES_BASE'] :
                dictCTRLSummary[key] = self.stanDict[key][0]

        dictTPSummary.to_excel('TP_summary.xlsx')
        dictCTRLSummary.to_excel('CTRL_summary.xlsx')
        # print(dictCTRLSummary)
        
        PYTEST.extractEntryData.extractEntryData(self.stanDict, 'stanDict', self.configurations['SET_MASTER'])
        

    def extractParameters(self, printOut=False):
        
        '''
        Extract parameters from trained model
        '''
        #pd.DataFrame(self.extractFrame.mean(axis=0)).to_csv('extractFrame.csv')
        self.parameters = {}
        self.num_touchpoints = self.stanDict['num_touchpoints']

        #Collect general model parameters and summarize in dictionary
        self.parameters['tau'] = self.extractFrame[f'tau'].mean(axis=0)
        self.parameters['noise_var'] = self.extractFrame['noise_var'].mean(axis=0)
        
        #self.extractFrame.mean().to_csv('estimatedParameters.csv')
        #print(self.extractFrame.mean())

        #Create seasonality variable
        for i, season in enumerate(self.configurations['SEASONALITY_VARIABLES_BASE'],start = 1):
            #append to general parameters list
            self.parameters[f'{season}_beta'] = self.extractFrame[f'beta_seasonality.{i}'].mean(axis=0)
            #append to easy access beta_seasonality list
            self.beta_seasonality.append(self.extractFrame[f'beta_seasonality.{i}'].mean(axis=0))
        
        #Create control variable
        for i, control in enumerate(self.configurations['CONTROL_VARIABLES_BASE'],start = 1):
            #append to general parameters list
            #self.parameters[f'{control}_beta'] = self.extractFrame[f'beta_control.{i}'].mean(axis=0)
            self.parameters[f'{control}_beta'] = self.extractFrame[f'beta_{control}'].mean(axis=0)
            #append to easy access beta_control list
            #self.beta_control.append(self.extractFrame[f'beta_control.{i}'].mean(axis=0))
            self.beta_control.append(self.extractFrame[f'beta_{control}'].mean(axis=0))

        for i, touchpoint in enumerate(self.configurations['TOUCHPOINTS'],start = 1):

            peak = self.extractFrame[f'peak.{i}'].mean(axis=0)
            decay = self.extractFrame[f'decay.{i}'].mean(axis=0)
            beta = self.extractFrame[f'beta_{touchpoint}'].mean(axis=0)


            #Collect per touchpoint parameters in dictionary
            self.parameters[f'{touchpoint}_adstock'] = {
                'L': self.responseModelConfig['MAX_LAG'],
                #'P': peak,
                'D': decay
            }


            shape = self.extractFrame[f'shape.{i}'].mean(axis=0)
            scale = self.extractFrame[f'scale.{i}'].mean(axis=0)


            self.parameters[f'{touchpoint}_shape'] = {
                'shape': shape,
                'scale': scale
            }

            self.parameters[f'{touchpoint}_beta']  = beta

            #definition of easy access variable(s)
            self.beta.append(beta)

            #if print is True specified, results will be printed here
            if (printOut == True):
                print()
                print(touchpoint+' --------')
                print()
                print("beta_2_coefficient")
                print(f"value:{beta}")
                print()
                print("adstock_touchpoint")
                print(f"value decay:{decay}")
                #print(f"value peak:{peak}")
                print()
                print("shape_touchpoint")
                print(f"value shape:{shape}")
                print(f"value scale:{scale}")
                print()

        if (printOut == True):
            for control in self.configurations['CONTROL_VARIABLES_BASE']:
                print(f'beta_{control}: ')
                print(self.parameters[f'{control}_beta'])

        return 0

    def transform(self, df):
        
        # tran_df = pd.DataFrame(df.iloc[:,:70].mean())
        tran_df = pd.DataFrame(df.mean())
        tran_df.to_excel('estimatedParametersMean.xlsx')
  

        return tran_df

    def runModel(self, name, load=True):
        '''
        Run stan model with created dictionary and save results
        '''

        if(load==False):
            posterior = stan.build(self.stanCode, data=self.stanDict)
            fit = posterior.sample(num_chains=4, num_samples=1000)
            self.extractFrame = fit.to_frame()
            self.extractFrame.to_csv(f'MODEL_SAVINGS/extract{name}.csv')
            self.transform(self.extractFrame)

        else:
            self.extractFrame = pd.read_csv(f'MODEL_SAVINGS/extract{name}.csv')
            self.transform(self.extractFrame)
            
        
        return 0
