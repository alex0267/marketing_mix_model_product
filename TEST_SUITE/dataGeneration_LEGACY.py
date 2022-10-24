import math
import matplotlib.pyplot as plt
import pandas as pd
import helper_functions.adstock_functions as adstock_functions
import helper_functions.hill_function
import helper_functions.normalization
import numpy as np
import yaml


def createIndex():
  week = pd.Series([x+1 for x in range(48)]*3)
  Y1 = pd.Series(['2020' for x in range(48)])
  Y2 = pd.Series(['2021' for x in range(48)])
  Y3 = pd.Series(['2022' for x in range(48)])

  #define years
  df = pd.DataFrame(Y1)
  df = pd.concat([df, Y2, Y3], axis=0)

  #define months
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


  df['week'] = week
  df.head()

  df['YEAR_WEEK'] = df[0]+ df['week'].astype(str)


  dummy = pd.get_dummies(pd.Series(monthList*3))
  df = df.reset_index(drop=True).rename(columns={0:'YEAR'})
  df = pd.concat([df,dummy], axis=1)

  return df


def simulateTouchpoints(touchpoints, configurations,responseModelConfig, format, baseSalesCoefficient_tp3 = 2500,baseSalesCoefficient_tp4=2500, plot = False):


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

#Iterate through all touchpoints that have been chosen to be included in the data generation process
  for touchpoint in touchpoints:
    
    if(touchpoint['control_var']=='month'):
      #define monthly seasonality influence
      #beta always 1 since direct influence unlike sales (defined via the factor parameter)
      #can be done for any month
      data[f'{touchpoint["name"]}{format}'] = controlFrame[touchpoint['name']]*touchpoint['factor']

      if plot == True:
        plt.plot(data[f'{touchpoint["name"]}{format}'][:subplot], color='blue')

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
      
      data[f'base_1{format}'] = base_1 + np.random.normal(0,noise_factor,weeks)
      if plot == True:
        plt.plot(data[f'base_1{format}'][:subplot], color='brown')
    
    if(touchpoint['name']=="base_2"):
      #Define touchpoint as sinusodial wave across the entire year
      
      #sin def
      for x in range(weeks):
        step = x+1
        size = ((2*math.pi)*step)/48
        time_col_pi.append(size)

      
      sin_wave = np.sin(time_col_pi)
      
      #Sinusodial sales - does not get adstocked but fits the definition
      data[f'base_2{format}'] = (sin_wave+2)*baseSalesCoefficient + np.random.normal(0,500,weeks)

      if plot == True:
        plt.plot(data[f'base_2{format}'][:subplot], color='brown')
           
    if(touchpoint ['name']=="touchpoint_2"):
      #Define touchpoint as pointed periodic spending throughout the year
      touchpoint_2 = []
      for x in range(weeks):
        if x%10 == 0: touchpoint_2.append(baseSalesCoefficient)
        else: touchpoint_2.append(0)

      #touchpoint definitions
      spendingsFrame["touchpoint_2"] = touchpoint_2

      data["touchpoint_2_adstocked"] = adstock_functions.apply_adstock_to_direct_spendings['touchpoint_2'](spendingsFrame["touchpoint_2"],touchpoint['L'], touchpoint['P'], touchpoint['D'])

      if plot == True:
        # plt.plot(spendingsFrame['touchpoint_2'][:subplot], color='blue')
        plt.plot(data["touchpoint_2_adstocked"][:subplot], color='green')
  
    if(touchpoint ['name']=="touchpoint_3"):
      #Define touchpoint as pointed periodic spending throughout the year
      touchpoint_3 = []
      for x in range(weeks):

        touchpoint_3.append(0)
        
        if x%4 == 0: 
          touchpoint_3[x] = touchpoint_3[x] + baseSalesCoefficient_tp3

        if x%26 == 0: 
          touchpoint_3[x] = touchpoint_3[x] + baseSalesCoefficient_tp3*1.5


      #touchpoint definitions
      spendingsFrame["touchpoint_3"] = touchpoint_3

      #apply adstock
      data["touchpoint_3_adstocked"] = adstock_functions.apply_adstock_to_direct_spendings['touchpoint_3'](spendingsFrame["touchpoint_3"],touchpoint['L'], touchpoint['P'], touchpoint['D'])
  
      #apply shape
      # print('T3 normal')
      # print((data["touchpoint_3_adstocked"]/spendingsFrame["touchpoint_3"].max())*5)
      # print('TP3 max')
      # print(spendingsFrame["touchpoint_3"].max())

      data["touchpoint_3_shaped"] = hillConversion(data["touchpoint_3_adstocked"],touchpoint, configurations, 25000)
      
      if plot == True:
        plt.plot(data["touchpoint_3_adstocked"][:subplot], color='green')
        plt.plot(data["touchpoint_3_shaped"][:subplot], color='black')
      
      # print('DATA HERE')

      #apply shape to spendings

    if(touchpoint ['name']=="touchpoint_4"):
      #Define touchpoint that has some semi random distribution patterns and periodic distribution patterns
      #Hill feature: spendings are relatively distributed in size providing a range of possible reference points for the hill estimation
      #Initial idea: this touchpoint is supposed to be covering the entire range of a hill distribution

      #define weeks in scope
      base_weeks = [2,5,7,10,15,18,20] 

      #define touchpoint spendings
      touchpoint_4 = []
      for x in range(weeks):
        
        touchpoint_4.append(0)
        #some short term periodic medium-sized touchpoint investments - middle-end of curve (depends on overcut with other investments)
        if x in np.arange(0, 157, 5).tolist(): 
          touchpoint_4[x] = touchpoint_4[x] + baseSalesCoefficient_tp4*2
        #some short term periodic low-end touchpoint investments - begin-middle of curve
        if x%4 == 0: 
          touchpoint_4[x] = touchpoint_4[x] + baseSalesCoefficient_tp4
        if x in [56,57,58,105,106,107]: 
          touchpoint_4[x] = touchpoint_4[x] + baseSalesCoefficient_tp4*2

        #some long term periodic high-end touchpoint  - end of curve
        if x%26 == 0: 
          touchpoint_4[x] = touchpoint_4[x] + baseSalesCoefficient_tp4*3.5
      
      #append to general spendings dataframe
      spendingsFrame["touchpoint_4"] = touchpoint_4

      #adstock spendings
      data["touchpoint_4_adstocked"] = adstock_functions.apply_adstock_to_direct_spendings(spendingsFrame["touchpoint_4"],touchpoint['L'], touchpoint['P'], touchpoint['D'])
      
      # print('TP4 max')
      # print(spendingsFrame["touchpoint_4"].max())
      #apply shape to spendings
      data["touchpoint_4_shaped"] = hillConversion(data["touchpoint_4_adstocked"],touchpoint, configurations, 65000)
      
      if plot == True:
        plt.plot(data["touchpoint_4_adstocked"][:subplot], color='pink')
        plt.plot(data["touchpoint_4_shaped"][:subplot], color='red')

    if(touchpoint ['name']=="touchpoint_5"):
        baseSalesCoefficient_tp5 = 2500
        #Define touchpoint as pointed periodic spending throughout the year
        touchpoint_5 = []
        for x in range(weeks):

          touchpoint_5.append(0)
          #for each week in scope, distribute the spendings over the following 4 weeks
          #we generate general spendings each two month that last a month
          if x%8 == 0 and x !=0: 
            touchpoint_5[x] = touchpoint_5[x] + baseSalesCoefficient_tp5
            touchpoint_5[x-1] = touchpoint_5[x-1] + baseSalesCoefficient_tp5
            touchpoint_5[x-2] = touchpoint_5[x-2] + baseSalesCoefficient_tp5
            touchpoint_5[x-3] = touchpoint_5[x-3] + baseSalesCoefficient_tp5
          #we generate half-year higher spendings that last a month
          if x%26 == 0 and x !=0: 
            touchpoint_5[x] = touchpoint_5[x] + baseSalesCoefficient_tp5*1.5
            touchpoint_5[x-1] = touchpoint_5[x-1] + baseSalesCoefficient_tp5*1.5
            touchpoint_5[x-2] = touchpoint_5[x-2] + baseSalesCoefficient_tp5*1.5
            touchpoint_5[x-3] = touchpoint_5[x-3] + baseSalesCoefficient_tp5*1.5

        #touchpoint definitions
        spendingsFrame["touchpoint_5"] = touchpoint_5

        

        #apply adstock
        data["touchpoint_5_adstocked"] = adstock_functions.apply_adstock_to_impression_spendings(spendingsFrame["touchpoint_5"],touchpoint['L'], touchpoint['D'])

        #normalize data
        data_normalized, data_norm = helper_functions.normalization.normalize_feature(data["touchpoint_5_adstocked"], spendingsFrame["touchpoint_5"], responseModelConfig['NORMALIZATION_STEPS_TOUCHPOINTS']['touchpoint_5'])

        max_spends = spendingsFrame["touchpoint_5"].max()
        #shape data

        data["touchpoint_5_shaped"] = helper_functions.hill_function.shape_function(data_normalized, 
                                                                                    shape = touchpoint['shape'], 
                                                                                    scale = touchpoint['scale'], 
                                                                                    threshold= touchpoint['threshold']/max_spends,
                                                                                    saturation = touchpoint['saturation']/max_spends)
        

        if plot == True:
          #plt.plot(spendingsFrame["touchpoint_5"][:subplot], color='blue')
          plt.plot((data["touchpoint_5_shaped"]*touchpoint['sales_saturation'])[:subplot], color='green')
          #plt.plot(data["touchpoint_5_shaped"][:subplot], color='black')
          
    if(touchpoint ['name']=="touchpoint_6"):
            baseSalesCoefficient_tp6 = 4000
            #Define touchpoint as pointed periodic spending throughout the year
            touchpoint_6 = []
            for x in range(weeks):

              touchpoint_6.append(0)
              #for each week in scope, distribute the spendings over the following 4 weeks
              #we generate general spendings each two month that last a month
              # if x%8 == 0 and x !=0: 
              #   touchpoint_6[x] = touchpoint_6[x] + baseSalesCoefficient_tp6
              #   touchpoint_6[x-1] = touchpoint_6[x-1] + baseSalesCoefficient_tp6
              #   touchpoint_6[x-2] = touchpoint_6[x-2] + baseSalesCoefficient_tp6
              #   touchpoint_6[x-3] = touchpoint_6[x-3] + baseSalesCoefficient_tp6
              #we generate half-year higher spendings that last a month
              if x%20 == 0 and x !=0: 
                touchpoint_6[x] = touchpoint_6[x] + baseSalesCoefficient_tp6*1.5
                touchpoint_6[x-1] = touchpoint_6[x-1] + baseSalesCoefficient_tp6*1.5
                touchpoint_6[x-2] = touchpoint_6[x-2] + baseSalesCoefficient_tp6*1.5
                touchpoint_6[x-3] = touchpoint_6[x-3] + baseSalesCoefficient_tp6*1.5

            #touchpoint definitions
            spendingsFrame["touchpoint_6"] = touchpoint_6



            #apply adstock
            data["touchpoint_6_adstocked"] = adstock_functions.apply_adstock_to_impression_spendings(spendingsFrame["touchpoint_6"],touchpoint['L'], touchpoint['D'])
            
            #normalize data
            data_normalized, data_norm = helper_functions.normalization.normalize_feature(data["touchpoint_6_adstocked"], spendingsFrame["touchpoint_6"], responseModelConfig['NORMALIZATION_STEPS_TOUCHPOINTS']['touchpoint_6'])

            max_spends = spendingsFrame["touchpoint_6"].max()
            #shape data
            data["touchpoint_6_shaped"] = helper_functions.hill_function.shape_function(data_normalized, 
                                                                                        shape = touchpoint['shape'], 
                                                                                        scale = touchpoint['scale'], 
                                                                                        saturation = touchpoint['saturation']/max_spends, 
                                                                                        threshold = touchpoint['threshold']/max_spends)

        
            if plot == True:
              #plt.plot(spendingsFrame["touchpoint_6"][:subplot]+spendingsFrame["touchpoint_5"][:subplot], color='blue')
              plt.plot((data["touchpoint_6_shaped"]*touchpoint['sales_saturation'])[:subplot], color='red')
              #plt.plot(data["touchpoint_6_shaped"][:subplot], color='red')

      #data[f"combination_{touchpoint['name']}"] = data[f"{touchpoint['name']}{format}"]*touchpoint['beta']


      #target model with "to_predict" beta variables


    data['sales'] = data['sales'] + data[f"{touchpoint['name']}{format}"]*touchpoint['sales_saturation']
    
    data[f"{touchpoint['name']}{format}_saturation"] = data[f"{touchpoint['name']}{format}"]*touchpoint['sales_saturation']

  controlFrame['promotion'] = 1

  #show
  if plot==True:
    plt.plot(data['sales'][:subplot], color='orange')
    plt.savefig('plots/data_generation.png')
    plt.clf()

  #return data - sales with respective adstocked spendings & influence parameters
  #return spendingsFrame - direct spendings per touchpoint
  #return controlFrame - dummy variable list of month variables
  index = controlFrame[['YEAR', 'YEAR_WEEK']]

  price_df = pd.Series([2 for x in range(len(spendingsFrame)) ])

  return data, price_df, spendingsFrame, controlFrame, index