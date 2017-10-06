import pdb
import pandas as pd
import numpy as np
import math

# file that you want to use
# be sure to change this before running the script
filename = "WhatsApp-chat met LustrumCie - 10 oktober.txt"
savename = "Lustrum_"

# open the file, decide upon encoding type.
f = open(filename, mode='r', encoding="utf8")
# initialise empty list to store the data, and empty counts for different errors
data = []

count_a, count_b = 0, 0
# loop over all lines in the text file
for line in f:
    # print each line for visual inspection
    print(line.strip())

    # attempt to split line
    try:
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
    datetime = date+time

    if text[:6] == 'U hebt':
        # If you are the group owner, this can change your actions to your name
        # if the owner changes somethins, name isn't registered that is fixed here
        name = 'Thomas Dolman'

    data.append([datetime, name, text])

# remove a bad timepoint
data[0][0] = data[1][0]
# get a pandas dataframe
df = pd.DataFrame(data, columns=["Date", "Name", "Text"])
# change index into timeseries.
df.Date = pd.to_datetime(df.Date, format='%Y-%m-%d')
df = df.set_index('Date')
if filename == "WhatsApp-chat met Congolezen.txt":
    # ugly way of removing this name from the dataframe
    df = df[df.Name != "Anneliek Ter Horst heeft een nieuw nummer"]

# returns number of posts per name sorted
df_count = df.groupby(by='Name').count().sort_values(by='Text')
# plot the number of times people sent messages and save the figure
import seaborn as sns
import matplotlib.pyplot as plt
plot_count = sns.countplot(x="Name", data=df)
plt.xticks(rotation=90)
plt.tight_layout()
plt.ylabel("Messages send")
import os
os.chdir('Output')
plt.savefig(savename + "Messages_send")

# check what words are said most, independent of by who
all_words_first = []
for sentence in df.Text:
    # create one list with all the words
    all_words_first.extend(sentence.strip().split(" "))

all_words = []
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
# hier kan nog iets leuks mee!!
# check categories, such as people
names_count = {}
names_out = {}
for person in df_count.index:
    try:
        person_first, person_second = person.lower().split(" ")
    except:
        try:
            person_first, addit, person_second = person.lower().split(" ")
        except:
            person_first, addit, addit2, person_second = person.lower().split(" ")

    names_count[person_first] = word_count[person_first]
    names_count[person_second] = word_count[person_second]
    names_out[person] = [word_count[person_first], word_count[person_second]]

df_names_mentioned = pd.DataFrame(names_out, index=['First_Name', 'Last_Name'])

# check when we are talking
df_weekly_count = df.resample('D').count()
df_weekly_count.plot()
plt.ylabel('Messages send')
plt.title("Messages send over time")
plt.savefig(savename + "When_we_talk")

# hier iets verzinnen
if filename == "WhatsApp-chat met Congolezen.txt":
    df_weekly_count.loc['2017-7-24':].plot()
    plt.ylabel('Messages send')
    plt.title("Messages send over time")
    plt.savefig(savename + "When_we_talk_zoomed")

# wanneer praten we onafhankelijk van de dag welk tijdstip
df_hour_count = df.resample('H').count()
df_hour_count['Date'] = df_hour_count.index.hour
hourly_act = {}
for ind in df_hour_count.index:
    try:
        hourly_act[df_hour_count.loc[ind,'Date']] += df_hour_count.loc[ind].Name
    except KeyError:
        hourly_act[df_hour_count.loc[ind, 'Date']] = df_hour_count.loc[ind].Name

ind = np.linspace(0, 23, 24)
df_hours = pd.DataFrame(hourly_act, index=ind)
df_hours = df_hours.iloc[0,:]
plt.close('all')
df_hours.plot(kind='bar')
plt.xlabel("Hour of the day")
plt.ylabel("Messages send")
plt.title("Time of the day")
plt.savefig(savename + "When_we_talk_per_hour")

# meeste fotos gestuurd.
who = []
for ind in range(1,len(df)-1):
    media = df.iloc[ind,1].find('Media')
    if media != -1:
        who.append([df.iloc[ind,0], 1])

df_media = pd.DataFrame(who, columns=['Name', 'Media_send'])
df_media_count = df_media.groupby(by='Name').count().sort_values(by='Media_send')
df_media_count.plot(kind='bar')
plt.ylabel("Images send")
plt.tight_layout()
plt.savefig(savename + "Images_send")
print(df_media_count)

# create output CSV by names showing messages send, media send, first name mention, last name mention
df_out = df_count.join(df_media_count)
df_out = df_out.join(df_names_mentioned.transpose())
df_out.to_csv(savename + "stats_per_name.csv")

