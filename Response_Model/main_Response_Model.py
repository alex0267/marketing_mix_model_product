import stan
import pandas as pd
import numpy as np
import helper_functions.normalization
import helper_functions.summarize

#class that contains the input and output data of a specific response model with respective model settings
#Also contains the functions to estimate and extract parameters
class ResponseModel:

    def __init__(self, spendingsFrame, controlFrame, configurations, responseModelConfig, target, stan_code):
        #define configurations
        self.configurations = configurations
        self.responseModelConfig = responseModelConfig

        #data
        self.controlFrame = controlFrame
        self.seasonality_df = self.controlFrame[configurations['SEASONALITY_VARIABLES_BASE']]
        self.otherControl_df = self.controlFrame[configurations['CONTROL_VARIABLES_BASE']]
        self.target = target #raw sales (target) variable with no transformation
        self.spendingsFrame = spendingsFrame #raw touchpoint spending data

        #define data normalized
        self.spendingsFrame_normalized, self.touchpoint_norms = helper_functions.normalization.normalize_feature(self.spendingsFrame,self.spendingsFrame, self.responseModelConfig['NORMALIZATION_STEPS_TOUCHPOINTS'])
        self.target_normalized, self.target_norm = helper_functions.normalization.normalize_feature(self.target,self.target, self.responseModelConfig['NORMALIZATION_STEPS_TARGET'][self.target.name])
        
        #easy access variables
        self.num_touchpoints = None
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

        #launch data extraction
        self.extractSummary()
        
    def extractSummary(self):

        responseModelInit_df = pd.DataFrame()

        for item in self.configurations['TOUCHPOINTS']:
            tp_df = pd.concat([self.controlFrame['YEAR_WEEK'],self.spendingsFrame[item].rename('spendings'),self.target], ignore_index=False, axis =1)
            tp_df['touchpoint'] = self.spendingsFrame[item].name
            #responseModelInit_df = responseModelInit_df.append(tp_df)
            responseModelInit_df = pd.concat([responseModelInit_df, tp_df], ignore_index=False,axis=0)

        print(responseModelInit_df)
        



        '''
        touchpoints=[]
        for item in self.configurations['TOUCHPOINTS']:
            summaryFrameself.spendingsFrame[item]
        

        target_to_add = pd.concat([self.controlFrame['YEAR_WEEK'],self.target], ignore_index=False, axis =1)

        summaryFrame = pd.concat([summaryFrame, self.spendingsFrame], ignore_index=False, axis=1).set_index('YEAR_WEEK')
        summaryFrame = self.spendingsFrame.stack()

        print(summaryFrame)
        # summaryFrame.to_excel('summaryFrame.xlsx')
        
        '''
    #create dictionary as input data for the stan model
    def createDict(self):

        num_touchpoints = len(self.configurations['TOUCHPOINTS'])
        touchpoint_norms = self.touchpoint_norms
        touchpoint_spendings = self.spendingsFrame[self.configurations['TOUCHPOINTS']]
        #add zeros to beginning of media dataframe to account for padding (weight application of adstock)
        touchpoint_spendings = np.concatenate((np.zeros((self.responseModelConfig['max_lag']-1, num_touchpoints)), np.array(touchpoint_spendings)),axis=0)

        self.stanDict = {
            'N': len(self.spendingsFrame),
            'max_lag': self.responseModelConfig['max_lag'], 
            'num_touchpoints': num_touchpoints,
            'touchpoint_spendings': touchpoint_spendings,
            'touchpoint_norms': touchpoint_norms,
            'touchpoint_thresholds': [self.responseModelConfig['SHAPE_THRESHOLD_VALUE'][tp] for tp in self.responseModelConfig['SHAPE_THRESHOLD_VALUE']],
            'touchpoint_saturations': [self.responseModelConfig['SHAPE_SATURATION_VALUE'][tp] for tp in self.responseModelConfig['SHAPE_SATURATION_VALUE']],
            'num_seasons': len(self.configurations['SEASONALITY_VARIABLES_BASE']),
            'seasonality': np.array(self.seasonality_df),
            # 'num_control': len(self.configurations['CONTROL_VARIABLES_BASE']),
            # 'control': np.array(responseModel.otherControl_df),
            'y': self.target_normalized.values
        }

    
    #extract parameters for each touchpoint
    def extractParameters(self, printOut=False):
        #pd.DataFrame(self.extractFrame.mean(axis=0)).to_csv('extractFrame.csv')
        self.parameters = {}
        self.num_touchpoints = self.stanDict['num_touchpoints']

        #Collect general model parameters and summarize in dictionary
        self.parameters['tau'] = self.extractFrame[f'tau'].mean(axis=0)
        self.parameters['noise_var'] = self.extractFrame['noise_var'].mean(axis=0)
        
        #self.extractFrame.mean().to_csv('estimatedParameters.csv')
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

    
