def constructEprosFeature(df, column):
    df = df[['YEAR_WEEK','BRAND',column]]
    df =df.rename(columns={column:'epros'})

    return df