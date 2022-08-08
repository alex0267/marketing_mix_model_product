import math
import matplotlib.pyplot as plt
import pandas as pd
import helper_functions.adstock_functions as adstock_functions
import helper_functions.hill_function
import Data_Preparation.normalization
import numpy as np
import yaml

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

  with open('test_suite/baseConfig.yaml', 'r') as file:
            configurations = yaml.safe_load(file)

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

      #set seed to reproduce error for each iteration
      np.random.seed(42)
      
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
  
      data["touchpoint_2_normalized"] = Data_Preparation.normalization.normalize_feature(data["touchpoint_2_adstocked"] , configurations['NORMALIZATION_STEPS_TOUCHPOINTS'][touchpoint ['name']], configurations, touchpoint ['name'])
      
      dt = data["touchpoint_2_normalized"]
      print('tp2')
      print(dt.mean())
      print(dt.min())
      print(dt.max())
      #hill_transformed_touchpoint = helper_functions.hill_function.hill_function(normalized_touchpoint, touchpoint['S'], touchpoint['H'])



    if(touchpoint ['name']=="touchpoint_3"):
      #Define touchpoint as pointed periodic spending throughout the year
      touchpoint_2 = []
      for x in range(weeks):
        if x%26 == 0: touchpoint_2.append(baseSalesCoefficient)
        else: touchpoint_2.append(0)

      #touchpoint definitions
      spendingsFrame["touchpoint_3"] = touchpoint_2

      data["touchpoint_3_adstocked"] = adstock_functions.apply_adstock(spendingsFrame["touchpoint_3"],touchpoint['L'], touchpoint['P'], touchpoint['D'])

      #plt.plot(spendingsFrame['touchpoint_2'][:subplot], color='blue')
      plt.plot(data["touchpoint_3_adstocked"][:subplot], color='green')
  
      data["touchpoint_3_normalized"] = Data_Preparation.normalization.normalize_feature(data["touchpoint_3_adstocked"] , configurations['NORMALIZATION_STEPS_TOUCHPOINTS'][touchpoint ['name']], configurations, touchpoint ['name'])
      
      dt = data["touchpoint_3_normalized"]
      print('tp2')
      print(dt.mean())
      print(dt.min())
      print(dt.max())
      # print('DATA HERE')



    if(touchpoint ['name']=="touchpoint_4"):
      #Define touchpoint that has some semi random distribution patterns and periodic distribution patterns
      #Hill feature: spendings are relatively distributed in size providing a range of possible reference points for the hill estimation
      #Initial idea: this touchpoint is supposed to be covering the entire range of a hill distribution

      #define weeks in scope
      base_weeks = [2,5,7,10,15,18,20] 

      #  = list(map(lambda x: x*2.5+max(a_list), a_list))

      touchpoint_4 = []
      for x in range(weeks):
        
        touchpoint_4.append(0)
        #some short term periodic medium-sized touchpoint investments - middle-end of curve (depends on overcut with other investments)
        if x in np.arange(0, 157, 5).tolist(): 
          touchpoint_4[x] = touchpoint_4[x] + baseSalesCoefficient*2
        #some short term periodic low-end touchpoint investments - begin-middle of curve
        if x%4 == 0: 
          touchpoint_4[x] = touchpoint_4[x] + baseSalesCoefficient
        if x in [56,57,58,105,106,107]: 
          touchpoint_4[x] = touchpoint_4[x] + baseSalesCoefficient*2

        #some long term periodic high-end touchpoint  - end of curve
        if x%26 == 0: 
          touchpoint_4[x] = touchpoint_4[x] + baseSalesCoefficient*3.5
      
      print((touchpoint_4))
      

      #touchpoint definitions
      spendingsFrame["touchpoint_4"] = touchpoint_4

      data["touchpoint_4_adstocked"] = adstock_functions.apply_adstock(spendingsFrame["touchpoint_4"],touchpoint['L'], touchpoint['P'], touchpoint['D'])

      #plt.plot(spendingsFrame['touchpoint_3'][:subplot], color='red')
      plt.plot(data["touchpoint_4_adstocked"][:subplot], color='pink')

      #print(data["touchpoint_3_adstocked"])

      data["touchpoint_4_normalized"] = Data_Preparation.normalization.normalize_feature(data["touchpoint_4_adstocked"] , configurations['NORMALIZATION_STEPS_TOUCHPOINTS'][touchpoint ['name']], configurations, touchpoint ['name'])
      
      dt = data["touchpoint_4_normalized"]
      print('tp3')
      print(dt.mean())
      print(dt.min())
      print(dt.max())

      d = pd.DataFrame([data["touchpoint_4_adstocked"],data["touchpoint_4_normalized"] ])
      d.to_csv('comp.csv')





      #target model with "to_predict" beta variables
    data['sales'] = data['sales'] + data[f"{touchpoint['name']}{format}"]*touchpoint['beta']

 
  # print(data)
  #add noise
  #data['sales'] = data['sales'] + np.random.normal(0,500,weeks)

  controlFrame['promotion'] = 1

  #show
  plt.plot(data['sales'][:subplot], color='orange')
  plt.show()
  plt.savefig('data_generation.png')

  #return data - sales with respective adstocked spendings & influence parameters
  #return spendingsFrame - direct spendings per touchpoint
  #return controlFrame - dummy variable list of month variables
  return data, spendingsFrame, controlFrame.iloc[:,4:]