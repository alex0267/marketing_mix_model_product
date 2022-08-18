import stan
import pandas as pd
import numpy as np
import helper_functions.normalization

#class that contains the input and output data of a specific response model with respective model settings
#Also contains the functions to estimate and extract parameters
class ResponseModel:

    def __init__(self, spendingsFrame, controlFrame, seasonalityFrame, configurations, responseModelConfig, target, stan_code):
        #define configurations
        self.configurations = configurations
        self.responseModelConfig = responseModelConfig

        #data
        self.seasonality_df = seasonalityFrame
        self.otherControl_df = controlFrame
        self.target = target #raw sales (target) variable with no transformation
        self.spendingsFrame = spendingsFrame #raw touchpoint spending data

        #define data normalized
        self.spendingsFrame_norm = helper_functions.normalization.normalize_feature(self.spendingsFrame, self.responseModelConfig['NORMALIZATION_STEPS_TOUCHPOINTS'], self.responseModelConfig)
        self.target_norm = helper_functions.normalization.normalize_feature(self.target, self.responseModelConfig['NORMALIZATION_STEPS_TARGET'], self.responseModelConfig)
        
        #easy access variables
        self.num_media = None
        self.beta = []
        self.beta_seasonality = []

        #contains the output estimated variables
        self.extractFrame = None  #contains the raw bayesian estimations
        self.parameters = None  #contains the summarized estimated parameters
        self.controlParameters = None

        #Define stan dictionary used for the stan model
        self.stanDict = None
        self.createDict()

        #Define stan code
        self.stan_code = stan_code
        

    
    #create dictionary as input data for the stan model
    def createDict(self):


        num_media = len(self.configurations['TOUCHPOINTS'])
        media_norm = np.array(self.spendingsFrame[self.configurations['TOUCHPOINTS']].max())
        X_media = self.spendingsFrame[self.configurations['TOUCHPOINTS']]
        #add zeros to beginning of media dataframe to account for padding (weight application of adstock)
        X_media = np.concatenate((np.zeros((self.responseModelConfig['max_lag']-1, num_media)), np.array(X_media)),axis=0)

        self.stanDict = {
            'N': len(self.spendingsFrame),
            'max_lag': self.responseModelConfig['max_lag'], 
            'num_media': num_media,
            'X_media': X_media,
            'media_norm': media_norm,
            'num_seasons': len(self.configurations['SEASONALITY_VARIABLES_BASE']),
            'seasonality': np.array(self.seasonality_df),
            # 'num_control': len(self.configurations['CONTROL_VARIABLES_BASE']),
            # 'control': np.array(responseModel.otherControl_df),
            'y': self.target_norm.values
        }


    
    #extract parameters for each touchpoint
    def extractParameters(self, printOut=False):
        pd.DataFrame(self.extractFrame.mean(axis=0)).to_csv('extractFrame.csv')
        self.parameters = {}
        self.num_media = self.stanDict['num_media']

        #Collect general model parameters and summarize in dictionary
        self.parameters['tau'] = self.extractFrame[f'tau'].mean(axis=0)
        self.parameters['noise_var'] = self.extractFrame['noise_var'].mean(axis=0)
        
        self.extractFrame.mean().to_csv('estimatedParameters.csv')
        #print(self.extractFrame.mean())

        for i, season in enumerate(self.configurations['SEASONALITY_VARIABLES_BASE'],start = 1):
            #append to general parameters list
            self.parameters[f'{season}_beta'] = self.extractFrame[f'beta_seasonality.{i}'].mean(axis=0)
            #append to easy access beta_seasonality list
            self.beta_seasonality.append(self.extractFrame[f'beta_seasonality.{i}'].mean(axis=0))

        for i, touchpoint in enumerate(self.configurations['TOUCHPOINTS'],start = 1):

            peak = self.extractFrame[f'peak.{i}'].mean(axis=0)
            decay = self.extractFrame[f'decay.{i}'].mean(axis=0)
            beta = self.extractFrame[f'beta.{i}'].mean(axis=0)


            #Collect per touchpoint parameters in dictionary
            self.parameters[f'{touchpoint}_adstock'] = {
                'L': self.responseModelConfig['max_lag'],
                'P': peak,
                'D': decay
            }

            slope = self.extractFrame[f'S.{i}'].mean(axis=0)
            half = self.extractFrame[f'H.{i}'].mean(axis=0)

            #Collect per touchpoint parameters in dictionary
            self.parameters[f'{touchpoint}_shape'] = {
                'S': slope,
                'H': half
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
                print(f"value peak:{peak}")
                print()
                print("shape_touchpoint")
                print(f"value slope:{slope}")
                print(f"value half:{half}")
                print()

        if (printOut == True):
            for season in self.configurations['SEASONALITY_VARIABLES_BASE']:
                print(f'beta_{season}: ')
                print(self.parameters[f'{season}_beta'])

        return 0


    def runModel(self, name, load=True):

        if(load==False):

            posterior = stan.build(self.stan_code, data=self.stanDict)
            fit = posterior.sample(num_chains=4, num_samples=1000)
            self.extractFrame = fit.to_frame()
            self.extractFrame.to_csv(f'model_savings/extract{name}.csv')

        else:
            self.extractFrame = pd.read_csv(f'model_savings/extract{name}.csv')
        
        return 0

    
