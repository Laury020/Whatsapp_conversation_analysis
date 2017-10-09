def Master(filename):
    """ This runs all the computations and plots all the figures
    """

    # note that ending on a number won't work
    savename = filename[18:-4] + "_"

    # load in the relevant data and turn it into a pandas DataFrame
    import analysis

    # load the text
    df = analysis.loadtext(filename)
    # count the words
    df_count = analysis.textanalysis(df, savename)
    # check who gets mentioned
    df_names_mentioned = analysis.analysewords(df, df_count)
    # see messages over time
    analysis.timeanalysis(df, savename)
    # count media send
    df_media_count = analysis.mediasend(df,savename)

    # create output CSV by names showing messages send, media send, first name mention, last name mention
    df_out = df_count.join(df_media_count)
    df_out = df_out.join(df_names_mentioned.transpose())
    df_out.to_csv(savename + "stats_per_name.csv")

    import os
    os.chdir('..')

if __name__=='__main__':
    Master()