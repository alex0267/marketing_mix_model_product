import pandas as pd
import os


directory_1 = 'TEST_SUITE/COMPARE_FRAMES/UPLIFT_COMPARISON_ALL_1'
directory_2 = 'TEST_SUITE/COMPARE_FRAMES/UPLIFT_COMPARISON_ALL_2'
directory_3 = 'TEST_SUITE/COMPARE_FRAMES/UPLIFT_COMPARISON_ALL_3'


def createFrame(directory):
    df = pd.DataFrame()
    for file in os.listdir(directory):

        if(str(file)[:10] == 'prediction'):
            f = pd.read_csv(f'{directory}/{file}')
            df = pd.concat([df,f], axis=0)

    return df.iloc[:,1:].rename(columns={'0':str(directory)[33:]})

def compareTables(df1,df2):
    total_df = pd.concat([df1,df2], axis =1)
    total_df = total_df.loc[~(total_df==0).all(axis=1)]
    total_df['DIFF'] = total_df.iloc[:,0]- total_df.iloc[:,1]
    total_df['AVG'] = (total_df.iloc[:,0]+total_df.iloc[:,1])/2 
    total_df['REL_DIFF'] =total_df['DIFF']/total_df['AVG']

    print(total_df.describe())
    print(f"quantile 0.8 : {total_df['REL_DIFF'].quantile(q=0.8)}")
    print(f"quantile 0.9 : {total_df['REL_DIFF'].quantile(q=0.9)}")
    print(f"quantile 0.95 : {total_df['REL_DIFF'].quantile(q=0.95)}")

    return total_df
    # print(together)


df_1 = createFrame(directory_1)
df_2 = createFrame(directory_2)
df_3 = createFrame(directory_3)

total1_2 = compareTables(df_1,df_2)
print('')
total1_3 = compareTables(df_1,df_3)
print('')
total2_3 = compareTables(df_2,df_3)

# print(total1_2.quantile(q=0.95))

# pd.read_csv(f'MODEL_SAVINGS/extract{name}.csv')