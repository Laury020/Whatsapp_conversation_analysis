def analysewords(df, df_count):
    """
    check what words are said most, independent by whom
    :param df: The data in a pandas dataframe
    :param df: the data 
    :return: the names that are said 
    """

    all_words_first, all_words = [], []
    for sentence in df.Text:
        # create one list with all the words
        all_words_first.extend(sentence.strip().split(" "))

    for word in all_words_first:
        # loop over each word and change it into lower case.
        all_words.append(word.lower())

    # get solely the unique words
    unique_words = set(all_words)

    # print some useful info
    print("the total number of unique words is: {} out of {} total words".format(len(unique_words), len(all_words)))
    print("Thus {} % is unique".format(round(100*len(unique_words)/len(all_words),3)))

    # get the occurrence of each word
    from collections import Counter
    word_count = Counter(all_words)
    # remove junk
    del word_count['<media']
    del word_count['weggelaten>']
    # show results
    print(word_count)

    # check categories, such as people
    names_count = {}
    names_out = {}
    for person in df_count.index:
        try:
            person_first, person_second = person.lower().split(" ")
        except ValueError:
            try:
                person_first, addit, person_second = person.lower().split(" ")
            except ValueError:
                try:
                    person_first, addit, addit2, person_second = person.lower().split(" ")
                except ValueError:
                    try:
                        person_first, addit, addit2, addit3, person_second = person.lower().split(" ")
                    except ValueError:
                        person_first = person
                        person_second = person

        names_count[person_first] = word_count[person_first]
        names_count[person_second] = word_count[person_second]
        names_out[person] = [word_count[person_first], word_count[person_second]]

    import pandas as pd
    df_names_mentioned = pd.DataFrame(names_out, index=['First_Name', 'Last_Name'])

    return df_names_mentioned

def loadtext(filename):
    import numpy as np
    import pandas as pd

    # open the file, decide upon encoding type.
    f = open(filename, mode='r', encoding="utf8")
    # initialise empty list to store the data, and empty counts for different errors
    data = []

    Group_Owner = input("If you are the owner of the group, type your name here: ")

    #check type of phone used, the text output is different.
    device = input("Is your device an Iphone (i) or an Android (a)? ")

    count_a, count_b = 0, 0
    # loop over all lines in the text file
    for line in f:
        # print each line for visual inspection
        print(line.strip())

        if device == 'i':
            if len(line)<3:
                continue
            try:
                datetime, name, text = line.split(": ")
                date_t, time = datetime.split(" ")
            except ValueError:
                try:
                    datetime, content = line.split(": ")
                    date_t, time = datetime.split(" ")
                    try:
                        name, text = content.split(": ")
                    except ValueError:
                        name = np.nan
                        text = content
                except ValueError:
                    try:
                        datetime, name, content, content1 = line.split(": ")
                        text = content + ": " + content1
                        date_t, time = datetime.split(" ")
                    except ValueError:
                        text = line


        elif device == 'a':
            try:
                # attempt to split line
                datetime, content = line.split(" - ")
                date_t, time = datetime.split(",")
                # if this works, continue by splitting the content
                try:
                    name, text = content.split(": ")
                    # otherwise store no name
                except ValueError:
                    name = np.nan
                    text = content

            except ValueError:
                try:
                    # special cases, where there seems to be no text in the message
                    datetime_old, namedate, content = line.split(" - ")
                    name_old, datetime = namedate.split(": ")
                    date_t, time = datetime.split(",")
                    count_a += 1
                    try:
                        name, text = content.split(": ")
                    except ValueError:
                        name = np.nan
                        text = content
                    # sometimes the person uses an Enter, this cathes that problem
                except ValueError:
                    text = line
                    count_b += 1


        # reformate date information to suit Pandas Timeseries
        date = "20" + date_t[-2:] + "-" + date_t[3:5] + "-" + date_t[:2]
        datetime = date+" "+time


        # catch a known error
        # TODO find a better solution for this.

        if datetime == "20af-vr-Ik vanaf “borreltijd” gaat de CK gewoon dicht toch":
            datetime, content, content1 = line.split(" - ")
            content = content + content1
            name, text = content.split(": ")
            date_t, time = datetime.split(",")
            date = "20" + date_t[-2:] + "-" + date_t[3:5] + "-" + date_t[:2]
            datetime = date + time
        if datetime =='2022-21-20 okt' or datetime =='2012-11-10 nov':
            datetime = "2017-07-23 00:04:11"
            name = "Marloes Westerwoudt"
            text = "Inschrijven voor een weekend!!"

        if text[:6] == 'U hebt':
            # If you are the group owner, this can change your actions to your name
            # if the owner changes somethins, name isn't registered that is fixed here
            name = Group_Owner

        data.append([datetime, name, text])

    # remove a bad timepoint
    if device == 'a':
        data[0][0] = data[1][0]
    # get a pandas dataframe
    df = pd.DataFrame(data, columns=["Date", "Name", "Text"])
    # change index into timeseries.
    df.Date = pd.to_datetime(df.Date, format='%Y-%m-%d')
    df = df.set_index('Date')

    if filename == "WhatsApp-chat met Congolezen.txt" or filename == "WhatsApp-chat met Niet zo zeuren.txt":
        # ugly way of removing this name from the dataframe
        df = df[df.Name != "Anneliek Ter Horst heeft een nieuw nummer"]

    # returns number of posts per name sorted
    len_vec = []
    for ind in range(len(df)):
        len_vec.append(len(df.iloc[ind, 1]))

    df['Len_text'] = len_vec

    return df


def mediasend(df, savename):
    """

    :param df: 
    :param savename: 
    :return: 
    """
    import pandas as pd
    import matplotlib.pyplot as plt

    # meeste fotos gestuurd.
    who = []
    for ind in range(1, len(df) - 1):
        media = df.iloc[ind, 1].find('Media')
        if media != -1:
            who.append([df.iloc[ind, 0], 1])

    df_media = pd.DataFrame(who, columns=['Name', 'Media_send'])
    df_media_count = df_media.groupby(by='Name').count().sort_values(by='Media_send')

    # Iphone works differently with media not attached
    if len(df_media) != 0:
        df_media_count.plot(kind='bar')
        plt.ylabel("Images send")
        plt.tight_layout()
        plt.savefig(savename + "Images_send")
    print(df_media_count)

    return df_media_count


def textanalysis(df, savename):
    """
    Analyse the number of messages send and the total number of characters send.

    :param df: The data in a pandas dataframe 
    :param savename: The name of the whatsappgroup, this precedes the output to distinguish groups
    :return: 
    """

    import os
    import seaborn as sns
    import matplotlib.pyplot as plt
    # change folder to save directory
    os.chdir('Output')

    # group the dataframe by Name
    df_count = df.groupby(by='Name').count().sort_values(by='Text')
    df_count_len = df.groupby(by='Name').sum().sort_values(by='Len_text')
    # plot the number of times people sent messages and save the figure

    sns.countplot(x="Name", data=df)
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.ylabel("Messages send")
    plt.savefig(savename + "Messages_send")

    # same plot order low to high
    plt.figure()
    df_count.Text.plot(kind='bar')
    plt.ylabel("Messages send")
    plt.tight_layout()
    plt.savefig(savename + "Messages_send_ordered")

    # total number of characters send.
    plt.figure()
    df_count_len.plot(kind='bar')
    plt.ylabel('Text length')
    plt.tight_layout()
    plt.savefig(savename + "Length of all text")

    return df_count


def timeanalysis(df, savename):
    """
    Analyse when people are talking over the days
    analyse what hour of the day people are talking

    :param df: 
    :param savename: 
    :return: 
    """
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt

    # check when we are talking
    df_daily_count = df.resample('D').count()
    df_daily_count.plot()
    plt.ylabel('Messages send')
    plt.title("Messages send over time")
    plt.savefig(savename + "When_we_talk")

    # When do we talk independent of days or whom
    df_hour_count = df.resample('H').count()
    df_hour_count['Date'] = df_hour_count.index.hour
    hourly_act = {}
    for ind in df_hour_count.index:
        try:
            hourly_act[df_hour_count.loc[ind, 'Date']] += df_hour_count.loc[ind].Name
        except KeyError:
            hourly_act[df_hour_count.loc[ind, 'Date']] = df_hour_count.loc[ind].Name

    # save the data into a dataframe
    ind = np.linspace(0, 23, 24)
    df_hours = pd.DataFrame(hourly_act, index=ind)
    df_hours = df_hours.iloc[0, :]

    # plot the bar graph showing time per day and messages send
    plt.close('all')
    df_hours.plot(kind='bar')
    plt.xlabel("Hour of the day")
    plt.ylabel("Messages send")
    plt.title("Time of the day")
    plt.savefig(savename + "When_we_talk_per_hour")
