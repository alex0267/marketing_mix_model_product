import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as ticker


def touchpoint_spendings_per_brand(feature_df):

    #set index on year only

    f = plt.figure(figsize=(15, 15))

    #iterate through each brand and create plots
    for i,brand in enumerate(feature_df["BRAND"].unique()[6:]):
        ax = f.add_subplot(4, 3, i + 1)

        brand_df = feature_df[feature_df['BRAND']==brand]
        brand_df = brand_df.drop(["YEAR_WEEK"],axis=1)

        ax = sns.lineplot(data=brand_df,legend = False ,dashes = False)
        #only include 4 x-axis labels
        ax.xaxis.set_major_locator(ticker.LinearLocator(4))
        ax.set_title(brand)


    #set subplot spacing parameters
    plt.subplots_adjust(left=0.1,
                        bottom=0.1,
                        right=0.9,
                        top=0.9,
                        wspace=0.4,
                        hspace=0.4)

    plt.show()

def touchpoint_spendings(feature_df, touchpoints):
    data = feature_df.sum()[1:]
    ax = sns.barplot(data.index, data.values)
    plt.show()



