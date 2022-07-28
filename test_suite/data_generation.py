import math
import matplotlib.pyplot as plt
import pandas as pd
import helper_functions.adstock_functions as adstock_functions
import numpy as np


def simulateTouchpoints(touchpoints, format):

  #only display a year of the plot
  subplot = 52
  noise_param = 0.03
  baseSalesCoefficient = 10000
  weeks = 157
  time_col_pi = []

  data = pd.DataFrame()
  spendingsFrame = pd.DataFrame()
  data['sales'] =[0 for x in range(weeks)]

  for touchpoint in touchpoints:

    if(touchpoint['name']=='base_1'):
      base_1 = []
      for x in range(weeks):
        if x%10 == 0: touchpoint_2.append(baseSalesCoefficient)
        else: touchpoint_2.append(0)
    
    if(touchpoint['name']=="touchpoint_1"):
      #Define touchpoint as sinusodial wave across the entire year
      #sin def
      for x in range(weeks):
        step = x+1
        size = ((2*math.pi)*step)/52
        time_col_pi.append(size)

      
      data['sin_wave'] = np.sin(time_col_pi)
      
            #Sinusodial touchpoint spendings
      spendingsFrame['touchpoint_1'] = (data['sin_wave']+2)*baseSalesCoefficient + np.random.normal(0,500,weeks)

        #Convert touchpoint data with adstock parameters
      data["touchpoint_1_adstocked"] = adstock_functions.apply_adstock(spendingsFrame["touchpoint_1"], touchpoint['L'], touchpoint['P'], touchpoint['D'])

    if(touchpoint ['name']=="touchpoint_2"):
      #Define touchpoint as pointed periodic spending throughout the year
      touchpoint_2 = []
      for x in range(weeks):
        if x%10 == 0: touchpoint_2.append(baseSalesCoefficient)
        else: touchpoint_2.append(0)

      #touchpoint definitions
      spendingsFrame["touchpoint_2"] = touchpoint_2

      data["touchpoint_2_adstocked"] = adstock_functions.apply_adstock(spendingsFrame["touchpoint_2"],touchpoint['L'], touchpoint['P'], touchpoint['D'])

      #plt.plot(spendingsFrame['touchpoint_2'][:subplot], color='blue')
      plt.plot(data["touchpoint_2_adstocked"][:subplot], color='green')

    if(touchpoint ['name']=="touchpoint_3"):
      #Define touchpoint as pointed periodic spending throughout the year (copy of touchpoint_2 with different period)
      touchpoint_3 = []
      for x in range(weeks):
        if x%26 == 0: touchpoint_3.append(baseSalesCoefficient)
        else: touchpoint_3.append(0)

      #touchpoint definitions
      spendingsFrame["touchpoint_3"] = touchpoint_3

      data["touchpoint_3_adstocked"] = adstock_functions.apply_adstock(spendingsFrame["touchpoint_3"],touchpoint['L'], touchpoint['P'], touchpoint['D'])

      #plt.plot(spendingsFrame['touchpoint_3'][:subplot], color='red')
      plt.plot(data["touchpoint_3_adstocked"][:subplot], color='pink')


      #target model with "to_predict" beta variables
    data['sales'] = data['sales'] + data[f"{touchpoint['name']}{format}"]*touchpoint['beta']
  #add noise
  #data['sales'] = data['sales'] + np.random.normal(0,500,weeks)

  #show

  plt.plot(data['sales'][:subplot], color='orange')
  plt.show()

 
  return data, spendingsFrame