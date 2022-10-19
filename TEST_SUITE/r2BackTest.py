import yaml

import runPipeline

'''
Application of k-fold cross validation back test

goal:
Assure cobustness of the model my calculating the R2 only on a test sample

challenges:
- Covid period might need to be analysed seperately (start with back test from 2018- beginning of 2020 at first)

restrictions:
- k not multiple of years analysed (2018-2021 = 3)

'''


def runBackTest():

    #Define configurations to be used
    with open('CONFIG/testConfig.yaml', 'r') as file:
            testConfig = yaml.safe_load(file)

    


    runPipeline.run()
    return 0