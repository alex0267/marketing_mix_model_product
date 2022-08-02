import math
import matplotlib.pyplot as plt
import pandas as pd
import helper_functions.adstock_functions as adstock_functions
import numpy as np

def createIndex():
  week = pd.Series([x+1 for x in range(48)]*3)
  Y1 = pd.Series([f'Y{1}' for x in range(48)])
  Y2 = pd.Series([f'Y{2}' for x in range(48)])
  Y3 = pd.Series([f'Y{3}' for x in range(48)])

  df = pd.DataFrame(Y1)
  df = pd.concat([df, Y2, Y3], axis=0)
  df['week'] = week
  df.head()

  df['ind'] = df[0]+'_'+ df['week'].astype(str)



  months = [
  'january',
  'february',
  'march',
  'april',
  'may',
  'june',
  'july',
  'august',
  'september',
  'october',
  'november',
  'december'
  ]

  monthList = []
  for x in range(len(months)):
    for y in range(4):
      monthList.append(months[x])

  df['month'] = monthList*3
  dummy = pd.get_dummies(pd.Series(monthList*3))
  df = df.reset_index(drop=True).rename(columns={0:'year'})
  df = pd.concat([df,dummy], axis=1)

  return df


def simulateTouchpoints(touchpoints, format):

  controlFrame = createIndex()

  #only display a year of the plot
  subplot = 144

  #define standard parameters
  noise_param = 0.03
  baseSalesCoefficient = 10000
  weeks = 144
  
  time_col_pi = []
  data = pd.DataFrame()
  spendingsFrame = pd.DataFrame()
  data['sales'] =[0 for x in range(weeks)]

  for touchpoint in touchpoints:
    
    if(touchpoint['control_var']=='month'):
      #define monthly seasonality influence
      #beta always 1 since direct influence unlike sales (defined via the factor parameter)
      #can be done for any month
      data[f'{touchpoint["name"]}_adstocked'] = controlFrame[touchpoint['name']]*touchpoint['factor']

      plt.plot(data[f'{touchpoint["name"]}_adstocked'][:subplot], color='blue')

    if(touchpoint['name']=="base_1"):
      #define constant baseline sales independent from marketing activities
      #include noise parameter

      #baseline sales
      baseline = touchpoint['factor']
      base_1 = [baseline for x in range(weeks)]

      #percentual noise parameter (as SD of basesales)
      noise_factor = touchpoint['noise_percentage']*baseline
      
      data['base_1_adstocked'] = base_1 + np.random.normal(0,noise_factor,weeks)

      plt.plot(data['base_1_adstocked'][:subplot], color='brown')
    
    if(touchpoint['name']=="base_2"):
      #Define touchpoint as sinusodial wave across the entire year
      #sin def
      for x in range(weeks):
        step = x+1
        size = ((2*math.pi)*step)/48
        time_col_pi.append(size)

      
      sin_wave = np.sin(time_col_pi)
      
      #Sinusodial sales - does not get adstocked but fits the definition
      data['base_2_adstocked'] = (sin_wave+2)*baseSalesCoefficient + np.random.normal(0,500,weeks)

      plt.plot(data['base_2_adstocked'][:subplot], color='brown')
      
       
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

  print('DATA HERE')
  print(data)
  #add noise
  #data['sales'] = data['sales'] + np.random.normal(0,500,weeks)

  #show
  plt.plot(data['sales'][:subplot], color='orange')
  plt.show()
  plt.savefig('data_generation.png')

  #return data - sales with respective adstocked spendings & influence parameters
  #return spendingsFrame - direct spendings per touchpoint
  #return controlFrame - dummy variable list of month variables
  return data, spendingsFrame, controlFrame.iloc[:,4:]