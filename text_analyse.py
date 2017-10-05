import pdb
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

filename = "WhatsApp-chat met Congolezen.txt"
# filename = "months.txt"
f = open(filename, mode='r', encoding="utf8")
# file = open(filename)
# text = file.read().split(" ")
# f = open(filename)
data = []
count_a, count_b = 0, 0
for line in f:
    print(line.strip())
    try:
        datetime, content = line.split(" - ")
        try:
            name, text = content.split(":")
        except ValueError:
            name = np.nan
            text = content

    except ValueError:
        try:
            # special cases, where there seems to be no text in the message
            datetime_old, namedate, content = line.split(" - ")
            name_old, datetime = namedate.split(": ")
            count_a += 1
            try:
                name, text = content.split(":")
            except ValueError:
                name = np.nan
                text = content
        except ValueError:
            text = line
            count_b += 1

    data.append([datetime, name, text])

# get a pandas dataframe
df = pd.DataFrame(data, columns=["Date", "Name", "Text"])
# ugly way of removing this name from the dataframe
df = df[df.Name != "Anneliek Ter Horst heeft een nieuw nummer"]

# returns number of posts per name sorted
df_count = df.groupby(by='Name').count().sort_values(by='Date')
# plot the number of times people sent messages and save the figure
import seaborn as sns
import matplotlib.pyplot as plt
plot_count = sns.countplot(x="Name", data=df)
plt.xticks(rotation=90)
plt.tight_layout()
plt.savefig("Messages_send")


# check what words are said most, independent of by who
all_words_first = []
for sentence in df.Text:
    # create one list with all the words
    all_words_first.extend(sentence.strip().split(" "))

all_words = []
for word in all_words_first:
    all_words.extend(word.lower())

unique_words = set(all_words)

print("the total number of unique words is: {} out of {} total words".format(len(unique_words), len(all_words)))
print("Thus {} % is unique".format(round(100*len(unique_words)/len(all_words),3)))
from collections import Counter
word_count = Counter(all_words)
print(word_count)
pdb.set_trace()



# check when we are talking



# meeste fotos gestuurd.


# meest gezegde naam


pdb.set_trace()

