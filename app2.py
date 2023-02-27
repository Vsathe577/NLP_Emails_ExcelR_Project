
# -*- coding: utf-8 -*-
"""Balancing Copy of Working Project-P184-NLP-Emails.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1N9Wo9itU8yfbPPItCzoqHrZqXX33XsIF

# Project-P62-NLP-Emails
"""

# Import Libraries and dataset

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.feature_extraction.text import CountVectorizer 
from sklearn.feature_extraction.text import TfidfTransformer
import streamlit as st
from sklearn.metrics import classification_report

# Import Dataset
emails=pd.read_csv("emails")

etext=emails[['content','Class']]
etext=etext.astype('U')

## Data Cleaning

import re # regular expression
import string

def clean_text(text):
    '''Make text lowercase, remove text in square brackets, remove punctuation and remove words containing numbers.'''
    #text=text.lower()
    text=re.sub('\[.*?\]',' ',text)
    text=re.sub('[%s]'% re.escape(string.punctuation),' ',text)
    text=re.sub('\w*\d\w*',' ',text)
    text=re.sub('[0-9' ']+',' ',text)
    text=re.sub('[''""…]', ' ', text)
    text=re.sub('[\n]', ' ', text)
    text=re.sub('[\s]', ' ', text)
    return text

clean = lambda x: clean_text(x)

etext['content']=etext['content'].apply(clean)

#Removing Stopwords
import string
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords

stop_words = set(stopwords.words('english') + ['excelr', 'ect', 'com', 'hou', 'cc', 'td', 'http', 'www', 'font', 'original', 'message','subject', 'fw'])

etext['content'] = etext['content'].apply(lambda x: " ".join(term for term in x.split() if term not in stop_words))

# Data Preprocessing

### BOW word_count_matrix

def split_into_words(i):
    return (i.split(' '))

from sklearn.feature_extraction.text import CountVectorizer

# Preparing email texts into bow word count matrix format 
email_bow=CountVectorizer(analyzer=split_into_words).fit(etext.content)


# For all messages
all_emails_matrix=email_bow.transform(etext.content)


### TFIDF tokenizer

from sklearn.feature_extraction.text import TfidfTransformer

# Learning Term weighting and normalizing on entire emails
tfidf_transformer=TfidfTransformer().fit(all_emails_matrix)

# Preparing TFIDF for all emails
all_emails_tfidf=tfidf_transformer.transform(all_emails_matrix)


### Label Encoding the class

from sklearn import preprocessing

# label_encoder object knows how to understand word labels

le = preprocessing.LabelEncoder()
  
etext['Class']= le.fit_transform(etext['Class']) 


# Model Building

from sklearn.model_selection import train_test_split
x_train,x_test,y_train,y_test=train_test_split(all_emails_tfidf,etext['Class'],test_size=0.3,random_state=42)


### Data Balancing using SMOTE

# 1. Oversampling

import imblearn
from imblearn.over_sampling import SMOTE
oversample = SMOTE(random_state=42)

# transform the dataset
x_train_os,y_train_os=oversample.fit_resample(x_train,y_train)

# 2. Undersampling

from imblearn.under_sampling import RandomUnderSampler
undersample=RandomUnderSampler(random_state=42)

# transform the dataset
x_train_s,y_train_s=undersample.fit_resample(x_train_os,y_train_os)


## Logistic Regression Classifier Algorithm

from sklearn.linear_model import LogisticRegression
log = LogisticRegression()

model_log=log.fit(x_train_s,y_train_s)

train_pred_log=model_log.predict(x_train_s)
accuracy_train_log=np.mean(train_pred_log==y_train_s)
print('accuracy_train_log:',accuracy_train_log)

test_pred_log=model_log.predict(x_test)
accuracy_test_log=np.mean(test_pred_log==y_test)
print('accuracy_test_log:',accuracy_test_log)

from sklearn.metrics import classification_report

# print classification report
print(classification_report(y_test,test_pred_log))


# Model Deployent
st.title('Model Deployment: NLP Emails')

str_sentence = st.text_input('Input your email text here:')
sentence = pd.DataFrame({'content':str_sentence},index=[0])
sentence=sentence.astype('U')

def clean_text(text):
     text=re.sub('\[.*?\]',' ',text)
     text=re.sub('[%s]'% re.escape(string.punctuation),' ',text)
     text=re.sub('\w*\d\w*',' ',text)
     text=re.sub('[0-9' ']+',' ',text)
     text=re.sub('[''""…]', ' ', text)
     text=re.sub('[\n]', ' ', text)
     text=re.sub('[\s]', ' ', text)
     return text

clean = lambda x: clean_text(x)

sentence['content']=sentence['content'].apply(clean)

stop_words = set(stopwords.words('english') + ['excelr', 'ect', 'com', 'hou', 'cc', 'td', 'http', 'www', 'font', 'original', 'message','subject', 'fw'])

sentence['content'] = sentence['content'].apply(lambda x: " ".join(term for term in x.split() if term not in stop_words))

# Lemmatization

estrip = [content.strip() for content in sentence.content] # remove both the leading and the trailing characters
estrip = [content for content in estrip if content] # removes empty strings, because they are considered in Python as False

# Joining the list into one string/text
estrip_text=' '.join(estrip)

#Punctuation
no_punc_text = estrip_text.translate(str.maketrans('', '', string.punctuation)) 

#Tokenization
import nltk
nltk.download('punkt')

from nltk.tokenize import word_tokenize
text_tokens = word_tokenize(no_punc_text)

len(text_tokens)

# NLP english language model of spacy library
import spacy
nlp = spacy.load('en_core_web_sm',disable=['parser', 'ner'])

# lemmas being one of them, but mostly POS, which will follow later
doc = nlp(' '.join(text_tokens))

lemmas = [token.lemma_ for token in doc]

all_emails_matrix_sent=email_bow.transform(lemmas)

tfidf_transformer_sent=TfidfTransformer().fit(all_emails_matrix_sent)

all_emails_tfidf_sent=tfidf_transformer_sent.transform(all_emails_matrix_sent)

prediction=model_log.predict(all_emails_tfidf_sent)
result=prediction.all()

if result==False:
    st.error('This is a Abusive Email')
else:
    st.success('This is a Non Abusive Email')





