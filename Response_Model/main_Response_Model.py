import stan
import Response_Model.stan_file
import model_savings
import pandas as pd

#class that contains the input and output data of a specific response model with respective model settings
#Also contains the functions to estimate and extract parameters
class ResponseModel:

    def __init__(self,touchpoints, stanDict):
        #define touchpoints and parameters (later replaced by yaml config files)
        self.touchpoints = touchpoints
        self.max_length = 4
        self.stanDict = stanDict

        #contains the output estimated variables
        self.extractFrame = None  #contains the raw bayesian estimations
        self.parameters = None  #contains the summarized estimated parameters

    #extract parameters for each touchpoint
    def extractParameters(self):
        self.parameters = {}

        #Collect general model parameters and summarize in dictionary
        self.parameters['tau'] = self.extractFrame[f'tau'].mean(axis=0)
        self.parameters['noise_var'] = self.extractFrame['noise_var'].mean(axis=0)
 
        for i, touchpoint in enumerate(self.touchpoints,start = 1):

            peak = self.extractFrame[f'peak.{i}'].mean(axis=0)
            decay = self.extractFrame[f'decay.{i}'].mean(axis=0)
            beta = self.extractFrame[f'beta.{i}'].mean(axis=0)

            #Collect per touchpoint parameters in dictionary
            self.parameters[touchpoint['name']] = {
                'L': self.max_length,
                'P': peak,
                'D': decay,
                'B': beta
            }


            print()
            print(touchpoint['name']+' --------')
            print()
            print("beta_2_coefficient")
            print(f"value:{beta}")
            print()
            print("adstock_touchpoint")
            print(f"value decay:{decay}")
            print(f"original:{touchpoint['D']}")
            print(f"value peak:{peak}")
            print(f"original:{touchpoint['P']}")

        return 0

    def runModel(self, load=True):

        if(load==False):
            posterior = stan.build(Response_Model.stan_file.stan_code, data=self.stanDict)
            fit = posterior.sample(num_chains=4, num_samples=1000)
            self.extractFrame = fit.to_frame()
            self.extractFrame.to_csv('model_savings/extract.csv')

        else:
            self.extractFrame = pd.read_csv('model_savings/extract.csv')
        
        self.extractParameters()

        return 0
