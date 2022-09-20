import pandas as pd
#creates a grouped dataframe that contains all prices by year and brand
#elements can be accessed via: price_df.get_group(('angry_cat', '2019'))
def calculatePrice(sell_out_df, configurations):
    price_df = sell_out_df[['BRAND','YEAR_WEEK']]
    price_df['YEAR'] = sell_out_df['YEAR_WEEK'].astype(str).str[:4]
    price_df['PRICE'] =  sell_out_df['SALES_SO'] / sell_out_df['VOLUME_SO']

    #super hacky solution, would be better with groupby but this makes problems with the 'ALL' filtering for ROS
    #calculating average price per brand and year
    priceFrame = pd.DataFrame()
    for brand in price_df['BRAND'].unique():
        for year in price_df['YEAR'].unique():
            # print(price_df[price_df['BRAND']==brand])
            subset = price_df[price_df['BRAND']==brand]
            subset = subset[price_df['YEAR']==year]
            
            subset['AVERAGE'] = subset['PRICE'].mean()
            priceFrame = pd.concat([priceFrame, subset],axis=0)



    return priceFrame