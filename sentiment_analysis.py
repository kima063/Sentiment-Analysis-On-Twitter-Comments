# -*- coding: utf-8 -*-
"""Sentiment_Analysis.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1erYjbVS-P-SqvChvXb8JjmJ9zi6r2qmK
"""

#datasets are collected from analyticsvidhya.com
#here a tweet with label '0' is of positive sentiment while a tweet with label '1' is of negative sentiment

# Commented out IPython magic to ensure Python compatibility.
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import string
import nltk
import warnings 
from nltk import PorterStemmer
warnings.filterwarnings("ignore", category=DeprecationWarning)
# %matplotlib inline

df_train = pd.read_csv('train.csv')

df_train = df_train.copy()

df_train.shape

df_train.head(10)

df_test = pd.read_csv('test.csv')

df_test = df_test.copy()

df_test.shape

df_test.head(10)

#removing twitter handles
def remove_pattern(text,pattern):   
    # re.findall() finds the pattern i.e @user and puts it in a list for further task
    r = re.findall(pattern,text)
    
    # re.sub() removes @user from the sentences in the dataset
    for i in r:
        text = re.sub(i,"",text)
    
    return text

df_train['tweet'] = np.vectorize(remove_pattern)(df_train['tweet'], "@[\w]*") 
df_train.head()

#Removing Punctuations, Numbers, and Special Characters
df_train['tweet'] = df_train['tweet'].str.replace("[^a-zA-Z#]", " ")
df_train.head(10)

#removing short words
df_train['tweet'] = df_train['tweet'].apply(lambda x: ' '.join([w for w in x.split() if len(w)>3]))
df_train.head(10)

#tokenization
tokenized_tweet = df_train['tweet'].apply(lambda x: x.split())
tokenized_tweet.head()

#stemming
#from nltk import PorterStemmer

ps = PorterStemmer()
tokenized_tweet = tokenized_tweet.apply(lambda x: [ps.stem(i) for i in x])
tokenized_tweet.head()

#joining the words back
for i in range(len(tokenized_tweet)):
    tokenized_tweet[i] = ' '.join(tokenized_tweet[i])
df_train['tweet'] = tokenized_tweet
df_train.head()

"""GENERATING WORD CLOUD"""

from wordcloud import WordCloud,ImageColorGenerator
from PIL import Image
import urllib
import requests

#store the positive ones in the dataset
all_words_positive = ' '.join(text for text in df_train['tweet'][df_train['label']==0])

# combining the image with the dataset
Mask = np.array(Image.open(requests.get('http://clipart-library.com/image_gallery2/Twitter-PNG-Image.png', stream=True).raw))

image_colors = ImageColorGenerator(Mask)

# Now we use the WordCloud function from the wordcloud library 
wc = WordCloud(background_color='black', height=1500, width=4000,mask=Mask).generate(all_words_positive)

# Size of the image generated 
plt.figure(figsize=(10,20))


# interpolation is used to smooth the image generated 
plt.imshow(wc.recolor(color_func=image_colors),interpolation="hamming")

plt.axis('off')
plt.show()

#storing the negative ones into dataset
all_words_negative = ' '.join(text for text in df_train['tweet'][df_train['label']==1])

# combining the image with the dataset
Mask = np.array(Image.open(requests.get('http://clipart-library.com/image_gallery2/Twitter-PNG-Image.png', stream=True).raw))


# Here we take the color of the image and impose it over our wordcloud
image_colors = ImageColorGenerator(Mask)

#using the WordCloud function from the wordcloud library 
wc = WordCloud(background_color='black', height=1500, width=4000,mask=Mask).generate(all_words_negative)

# Size of the image generated 
plt.figure(figsize=(10,20))

# interpolation is used to smooth the image generated 
plt.imshow(wc.recolor(color_func=image_colors),interpolation="hamming")

plt.axis('off')
plt.show()

#func for extracting hashtags

def Hashtags_Extract(x):
    hashtags=[]
    
    # Loop over the words in the tweet
    for i in x:
        ht = re.findall(r'#(\w+)',i)
        hashtags.append(ht)
    
    return hashtags

#list of list of all the hashtags from the positive reviews from the dataset
ht_positive = Hashtags_Extract( df_train['tweet'] [df_train['label']==0])
ht_positive

ht_positive_unnest = sum(ht_positive,[])

#list of list of all the hashtags from the negative reviews from the dataset
ht_negative = Hashtags_Extract(df_train['tweet'] [df_train['label']==1])
ht_negative

ht_negative_unnest = sum(ht_negative,[])
ht_negative_unnest

#Counting the frequency of the words having Positive Sentiment

word_freq_positive = nltk.FreqDist(ht_positive_unnest)

# word_freq_positive

#Creating a dataframe for the most frequently used words in hashtags for positive words
df_positive = pd.DataFrame({'Hashtags':list(word_freq_positive.keys()),'Count':list(word_freq_positive.values())})

df_positive.head(10)

#Plotting the barplot for the 10 most frequent positive words used for hashtags
df_positive_plot = df_positive.nlargest(10,columns='Count') 
sns.barplot(data=df_positive_plot,y='Hashtags',x='Count')
sns.despine()

#Counting the frequency of the words having negative Sentiment
word_freq_negative = nltk.FreqDist(ht_negative_unnest)

# word_freq_negative

#Creating a dataframe for the most frequently used words in hashtags for negative words
df_negative = pd.DataFrame({'Hashtags':list(word_freq_negative.keys()),'Count':list(word_freq_negative.values())})

df_negative.head(10)

#Plotting the barplot for the 10 most frequent negative words used for hashtags
df_negative_plot = df_negative.nlargest(10,columns='Count') 
sns.barplot(data=df_negative_plot,y='Hashtags',x='Count')
sns.despine()

x = df_train['tweet']
y = df_train['label']

#Splitting the data into training and validation set
from sklearn.model_selection import train_test_split 
x_train,x_test,y_train,y_test = train_test_split(x ,y,test_size=0.3,random_state=17)

#TF-IDF Features
from sklearn.feature_extraction.text import TfidfVectorizer

tfidf=TfidfVectorizer(max_df=0.90, min_df=2,max_features=1000,stop_words='english')

tfidf_x_train =tfidf.fit_transform(x_train)

tfidf_x_test =tfidf.transform(x_test)

#using Logistic Regression
from sklearn.linear_model import LogisticRegression
Log_Reg = LogisticRegression(random_state=0,solver='lbfgs')
accuracy = 0
kfold = KFold(10, True, 1)
for train, test in kfold.split(x, y):
  Log_Reg.fit(tfidf_x_train , y_train)
  accuracy += Log_Reg.score(tfidf_x_test, y_test)
print("Average accuracy (using Logistic Regression) : ", accuracy/10)

#using multimonial Naive Bayes
from sklearn.naive_bayes import MultinomialNB 
accuracy = 0
kfold = KFold(10, True, 1)
for train, test in kfold.split(x, y):
  classifier = MultinomialNB().fit(tfidf_x_train , y_train)
  prediction = classifier.predict(tfidf_x_test)
  accuracy += accuracy_score(y_test, prediction)
print("Average accuracy (using multimonial Naive Bayes) : ", accuracy/10)