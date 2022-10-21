import stan
import pandas as pd
import numpy as np
import HELPER_FUNCTIONS.normalization
import HELPER_FUNCTIONS.summarize

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
        self.target_df_normalized, self.target_df_norm = HELPER_FUNCTIONS.normalization.normalize_feature(filteredFeature_df[configurations['TARGET']],filteredFeature_df[configurations['TARGET']], self.responseModelConfig['NORMALIZATION_STEPS_TARGET'][filteredFeature_df[configurations['TARGET']].name])
        
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
        
    
    def createDict(self):

        '''
        create dictionary as input data for the stan model
        '''
        num_touchpoints = len(self.configurations['TOUCHPOINTS'])
        touchpointSpend_df = self.filteredFeature_df[self.configurations['TOUCHPOINTS']]
        #add zeros to beginning of media dataframe to account for padding (weight application of adstock)
        touchpointSpend_df = np.concatenate((np.zeros((self.responseModelConfig['MAX_LAG']-1, num_touchpoints)), np.array(touchpointSpend_df)),axis=0)

        self.stanDict = {
            'N': len(self.filteredFeature_df[self.configurations['TOUCHPOINTS']]),
            'max_lag': self.responseModelConfig['MAX_LAG'], 
            'num_touchpoints': num_touchpoints,
            'touchpointSpend_df': touchpointSpend_df,
            'touchpointNorms': self.touchpointNorms,
            'touchpointThresholds': [self.responseModelConfig['SHAPE_THRESHOLD_VALUE'][tp] for tp in self.configurations['TOUCHPOINTS']],
            'touchpointSaturations': [self.responseModelConfig['SHAPE_SATURATION_VALUE'][tp] for tp in self.configurations['TOUCHPOINTS']],
            'num_seasons': len(self.configurations['SEASONALITY_VARIABLES_BASE']),
            'seasonality': np.array(self.filteredFeature_df[self.configurations['SEASONALITY_VARIABLES_BASE']]),
            'num_control': len(self.configurations['CONTROL_VARIABLES_BASE']),
            'control': np.array(self.filteredFeature_df[['YEAR_WEEK','BRAND','distribution', 'promotion', 'epros', 'covid','off_trade_visibility']]),
            'y': self.target_df_normalized.values
        }

    
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
            self.parameters[f'{control}_beta'] = self.extractFrame[f'beta_control.{i}'].mean(axis=0)
            #append to easy access beta_control list
            self.beta_control.append(self.extractFrame[f'beta_control.{i}'].mean(axis=0))

        for i, touchpoint in enumerate(self.configurations['TOUCHPOINTS'],start = 1):

            peak = self.extractFrame[f'peak.{i}'].mean(axis=0)
            decay = self.extractFrame[f'decay.{i}'].mean(axis=0)
            beta = self.extractFrame[f'beta.{i}'].mean(axis=0)


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

    def runModel(self, name, load=True):
        '''
        Run stan model with created dictionary and save results
        '''

        if(load==False):
            posterior = stan.build(self.stanCode, data=self.stanDict)
            fit = posterior.sample(num_chains=4, num_samples=1000)
            self.extractFrame = fit.to_frame()
            self.extractFrame.to_csv(f'MODEL_SAVINGS/extract{name}.csv')

        else:
            self.extractFrame = pd.read_csv(f'MODEL_SAVINGS/extract{name}.csv')
        
        return 0
