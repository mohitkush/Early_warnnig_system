# -*- coding: utf-8 -*-
"""EWS_guardian_optimized.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1FjzkPjYCrDZ2K_tcd3kBEYcslAWrS4l7
"""

import requests
import json
from datetime import date,timedelta, datetime
from tqdm import tqdm
import string
import re
from typing import List
import pandas as pd
import re
import numpy as np
# Get Metadata from gaurdian webpage
def get_articles(end_date: str, query: str):  
  edate = datetime.fromisoformat(end_date)
  #edate = datetime.fromisoformat(input("input start the end date (from which you want to check last 7 days data) in yyyy-mm-dd format:",))
  #edate = date(2022,11,1)
  #sdate = date(2022,3,1)
  sdate = edate - timedelta(days=7)
  from_date = str(sdate.year)+'-'+str(sdate.month)+'-'+str(sdate.day)
  to_date = str(edate.year)+'-'+str(edate.month)+'-'+str(edate.day)


  r = requests.get('https://content.guardianapis.com/search?'
                    'q='+query+'&'
                    'from-date='+from_date+'&'
                    'to-date='+to_date+'&'
                    'show-section=true&'
                    'show-fields=body&'
                    'show-tags=all&'
                    'api-key=f13a5535-68ce-40c0-a1fe-39304e9770c3')
  res = r.json()
  article_content = []
  for i in tqdm(range(1,res['response']['pages']+1)):
    ri = requests.get('https://content.guardianapis.com/search?'
                  'q='+query+'&'
                  'from-date='+from_date+'&'
                  'to-date='+to_date+'&'
  #                'tag=world/china&'
                  'show-fields=body&'
                  'page='+str(i)+'&'
                  'show-section=true&'
                  'show-tags=all&'
                  'api-key=f13a5535-68ce-40c0-a1fe-39304e9770c3')
    temp = ri.json()
    if temp['response']['status']!='error':
      for article in temp['response']['results']:
        if article['type'] != 'liveblog':
          article_dict = {}
          art = article['fields']['body']
          soup = BeautifulSoup(art)
          temp_str = ''
          try:
            for para in soup.find_all('p'):
              temp_str += para.text + " "
            article_dict['content'] =temp_str
            article_dict['webTitle'] = article['webTitle']
            date = datetime.fromisoformat(article['webPublicationDate'].replace('T',' ').replace('Z',''))
            article_dict['date'] = date
            article_dict['tag'] = article['section']['webTitle']
            article_dict['date_weight'] = 1 #1/(edate.day - date.day)
            article_dict['subtag'] = article['tags'][0]['webTitle']
            article_dict['link'] = article['webUrl']
            article_dict['tag_list'] = [tag['webTitle'] for tag in article['tags']]
            article_content.append(article_dict)
          except KeyError:
            print('fail')
            pass
  return article_content

# Define Weight dictionary with respect to each category of bag of words
weights = {'Supply Chain':2,	'Commodities':2,	'Client Specific Words':5,	'Automobile Indursty':4,	'Suppliers':5,	'War/ Calamities words':3, 'client specific location':4, 'exceptions':1}

import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from textblob import TextBlob
nltk.download('stopwords')
nltk.download('punkt')
stop_words = set(stopwords.words('english'))
from nltk.stem import RegexpStemmer
stemmer= RegexpStemmer('ing$|s$|e$|able$', min=4)

def bow_filtering(bag_of_words_df:pd.DataFrame):
  """ function to preprocess bag of words, returns a list of bag of words and two dictionary,
  first one has stemmed word as keys and it's category as values, second one has stemmed word as keys and original word as values"""
  bagofwords_dict = {}
  org_word = {}
  for i in list(bag_of_words_df['Supply Chain'].dropna()):
    res_bow = re.sub("[^-9A-Za-z ]", ' ', i).lower()
    temp = ' '.join([stemmer.stem(x) for x in res_bow.split()])
    org_word[temp] = i
    bagofwords_dict[temp] = 'Supply Chain'

  
  for i in list(bag_of_words_df['Commodities'].dropna()):
    res_bow = re.sub("[^-9A-Za-z ]", ' ', i).lower()
    temp = ' '.join([stemmer.stem(x) for x in res_bow.split()])
    org_word[temp] = i
    bagofwords_dict[temp] = 'Commodities'
  
  for i in list(bag_of_words_df['Client Specific Words'].dropna()):
    res_bow = re.sub("[^-9A-Za-z ]", ' ', i).lower()
    temp = ' '.join([stemmer.stem(x) for x in res_bow.split()])
    org_word[temp] = i
    bagofwords_dict[temp] = 'Client Specific Words'

  for i in list(bag_of_words_df['Automobile Indursty'].dropna()):
    res_bow = re.sub("[^-9A-Za-z ]", ' ', i).lower()
    temp = ' '.join([stemmer.stem(x) for x in res_bow.split()])
    org_word[temp] = i
    bagofwords_dict[temp] = 'Automobile Indursty'
  
  for i in list(bag_of_words_df['Suppliers'].dropna()):
    res_bow = re.sub("[^-9A-Za-z ]", ' ', i).lower()
    temp = ' '.join([stemmer.stem(x) for x in res_bow.split()])
    org_word[temp] = i
    bagofwords_dict[temp] = 'Suppliers'
  
  for i in list(bag_of_words_df['War/ Calamities words'].dropna()):
    res_bow = re.sub("[^-9A-Za-z ]", ' ', i).lower()
    temp = ' '.join([stemmer.stem(x) for x in res_bow.split()])
    org_word[temp] = i
    bagofwords_dict[temp] = 'War/ Calamities words'
  
  for i in list(bag_of_words_df['client specific location'].dropna()):
    res_bow = re.sub("[^-9A-Za-z ]", ' ', i).lower()
    temp = ' '.join([stemmer.stem(x) for x in res_bow.split()])
    org_word[temp] = i
    bagofwords_dict[temp] = 'client specific location'
  # Commenting the categories that we don't want to include in bag of words 
  # for i in list(bag_of_words_df['exceptions'].dropna()):
  #   if i not in stop_words:
  #     bagofwords_dict[stemmer.stem(i)] = 'exceptions'
  
  bagofwords = bagofwords_dict.keys()

  return bagofwords,bagofwords_dict,org_word

import spacy # just for sentence segmentation
nlp = spacy.load('en_core_web_sm') # just for sentence segmentation

import nltk
nltk.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer

def textblob(text):
  """ Function to calculate textblob polarity, subjectivity of a given text"""
  txb= TextBlob(text)
  pol= txb.sentiment.polarity
  sub= txb.sentiment.subjectivity
  return pol,sub


sid = SentimentIntensityAnalyzer()  
def vader(text):
  """ funciton to calculate vader compound, negative word ratio, positive word ratio and neutral word ratio"""
  txt= sid.polarity_scores(text)
  comp,neg,neu,pos = txt['compound'],txt['neg'],txt['neu'],txt['pos']
  return comp,neg,neu,pos


def generate_N_grams(words,ngram=1):
  """ function to generate ngrams of a given list of words"""
  temp=zip(*[words[i:] for i in range(0,ngram)])
  ans=[' '.join(ngram) for ngram in temp]
  return ans


def preprocessing_article(article,one_word_bow,two_word_bow,three_word_bow,bagofwords_dict,org_word):
  """Funciton to preprocess articles and calculation of sentence wise weighted vader score. This fucntion also checks for keywords matching in a sentence with the bag of words"""
  sentiments=[]
  article = article.lower()
  # Text cleaning of an article
  clean_text= article.replace("/", " ")       
  clean_text= ''.join([c for c in clean_text if c != "'"])
  sentence=[]
  # Sentence segmentation
  tokens = nlp(clean_text)
  #defining am empty dataframe to store results for each sentence of an article
  df_temp = pd.DataFrame(columns=['sentence','keyword','categories','category_score','textblob_polarity','textlob_subjectivity','vader_compund','vader_negativity','vader_nuetrality','vader_posotivity'])
  for sent in tokens.sents:
    cat_score = 1
    categ = []
    keyword = []
    # words =re.sub("[^\w\s]", ' ', sent).lower() # to remove punctuations from a sentence
    words = word_tokenize(sent.text.strip())
    # Word wise stemming
    words=[stemmer.stem(word) for word in words if word not in stop_words]
    #splitting words in to one, two and three grams words
    one_gram_data = generate_N_grams(words,ngram=1)
    two_gram_data = generate_N_grams(words,ngram=2)
    three_gram_data = generate_N_grams(words,ngram=3)

    # checking one gram words with one gram bag of words
    for dword in one_gram_data:
      for bword in one_word_bow:
        if dword == bword:
          keyword.append(org_word[bword])
          categ.append(bagofwords_dict[bword])
          cat_score += weights[bagofwords_dict[bword]]
    # checking two gram words with two gram bag of words
    for dword in two_gram_data:
      for bword in two_word_bow:
        if dword == bword:
          keyword.append(org_word[dword])
          categ.append(bagofwords_dict[dword])
          cat_score += weights[bagofwords_dict[dword]]
    # checking three gram words with three gram bag of words      
    for dword in three_gram_data:
      for bword in three_word_bow:
        if dword == bword:
          keyword.append(org_word[dword])
          categ.append(bagofwords_dict[dword])
          cat_score += weights[bagofwords_dict[dword]]
    # calculating textblob sentiment of the original sentence i.e. before stemming      
    txb_pol,txb_sub = textblob(sent.text)
    # calculating vader sentiment of the original sentence i.e. before stemming
    comp,neg,neu,pos = vader(sent.text) 
    df_temp.loc[len(df_temp)] = [sent,keyword, categ,cat_score,txb_pol,txb_sub,comp,neg,neu,pos]
  #Check if no keywords is found for an article, return nan values for it so that we can drop these article
  if len(df_temp['categories'].sum())==0:
    return [np.nan]*9
  else:
    #extracting keywords, and categories for the whole document
    keywords,categories,cat_scores = df_temp['keyword'].sum(),df_temp['categories'].sum(),df_temp['category_score'].sum()
    #filtering out neutral sentences
    df_temp = df_temp[(df_temp['vader_compund']>0.1) | (df_temp['vader_compund']<-0.1)]
    #calculating weighted average
    comp = sum(df_temp['vader_compund']*df_temp['category_score'])/sum(df_temp['category_score'])
    neg = sum(df_temp['vader_negativity']*df_temp['category_score'])/sum(df_temp['category_score'])
    neu = sum(df_temp['vader_nuetrality']*df_temp['category_score'])/sum(df_temp['category_score'])
    pos = sum(df_temp['vader_posotivity']*df_temp['category_score'])/sum(df_temp['category_score'])
    txt_pol = sum(df_temp['textblob_polarity']*df_temp['category_score'])/sum(df_temp['category_score'])
    txt_sub = sum(df_temp['textlob_subjectivity']*df_temp['category_score'])/sum(df_temp['category_score'])
    return [keywords,categories,cat_scores,comp,neg,neu,pos,txt_pol,txt_sub]

#Get articles metadata
article_content = get_articles("2022-06-12","China")
#convert it into a dataframe
df_article = pd.DataFrame(article_content)

#bag of words
sheet_id = "1obKSC3mXySGbjJ7OV7Iw8tswNEHHLU5NP0f2gsnKT7g"
sheet_name = "Sheet5"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
bag_of_words_df = pd.read_csv(url)
bagofwords, bagofwords_dict,org_word = bow_filtering(bag_of_words_df)
one_word_bow = [x for x in bagofwords if len(x.split())==1]
two_word_bow = [x for x in bagofwords if len(x.split())==2]
three_word_bow = [x for x in bagofwords if len(x.split())==3]

#tag list filter
selection = ['China']
df_subtag_article = df_article[df_article.tag_list.apply(lambda x: any(item for item in selection if item in x))]

#Aplying preprocessing an keywords matching for all the articles
columns = ['keywords','categories','category_score','vader_weighted_compound','vader_weighted_negativity','vader_weighted_neutrality','vader_weighted_positivity','textblob_weighted_polarity','textblob_weighted_subjectivity']
for i in tqdm(df_subtag_article.index):
  df_subtag_article.loc[i,columns] = preprocessing_article(df_subtag_article['content'][i],one_word_bow,two_word_bow,three_word_bow,bagofwords_dict,org_word)

# Dropping ariticle with no keywords match
df_subtag_article = df_subtag_article.dropna()


# df_atleast_twocat = df_final[df_final['categories'].apply(set).apply(set).apply(len)>1]

"""## TF-IDF of the whole corpus"""

import math
from numpy import linalg as LA

# compute Term frequency of a specific term in a document
def termFrequency(term, document):
    normalizeDocument = document.lower().split()
    return normalizeDocument.count(term.lower()) / float(len(normalizeDocument))
    
# IDF of a term
def inverseDocumentFrequency(term, documents):
    count = 0
    for doc in documents:
        if term.lower() in doc.lower().split():
            count += 1
    if count > 0:
        return 1.0 + math.log(float(len(documents))/count)
    else:
        return 1.0       

# tf-idf of a term in a document
def tf_idf(term, document, documents):
    tf = termFrequency(term, document)
    idf = inverseDocumentFrequency(term, documents)
    return tf*idf


def generateVectors(query, documents):
    tf_idf_matrix = np.zeros((len(query), len(documents)))
    for i, s in enumerate(query):
        idf = inverseDocumentFrequency(s.lower(), documents)
        for j,doc in enumerate(documents):
            tf_idf_matrix[i][j] = idf * termFrequency(s.lower(), doc)
    return tf_idf_matrix

def temp(sent):  
  words = word_tokenize(sent.strip())
  words=[stemmer.stem(word) for word in words if word not in stop_words]
  return ' '.join(words)

def word_count(s):
    counts = dict()
    words = s
    for word in words:
        if word.lower() in counts:
            counts[word] += 1
        else:
            counts[word] = 1
    return counts

def build_query_vector(query, documents):
    count = word_count(query)
    vector = np.zeros((len(count),1))
    for i, word in enumerate(query):
        vector[i] = float(count[word])/len(count) * inverseDocumentFrequency(word, documents)
    return vector


def consine_similarity(v1, v2):
    return np.dot(v1,v2)/float(LA.norm(v1)*LA.norm(v2))

documents = df_subtag_article['content'].str.lower().apply(temp)
lis = (list(set([a for b in df_subtag_article.keywords.tolist() for a in b])))
tf_idf_matrix = generateVectors(lis, documents)

query_vector = build_query_vector(lis, documents)

tfidf_scores = pd.DataFrame(tf_idf_matrix.T,columns=lis)
tfidf_scores['cosine_simi_no_weight'] = 0

for i, doc in enumerate(documents):
  similarity = consine_similarity(tf_idf_matrix[:,i].reshape(1, len(tf_idf_matrix)), query_vector)
  tfidf_scores.loc[i,'cosine_simi_no_weight'] = float(similarity[0])

for col in list(set(lis)):
  res_bow = re.sub("[^-9A-Za-z ]", ' ', col).lower()
  temp = ' '.join([stemmer.stem(x) for x in res_bow.split()])
  cat = bagofwords_dict[temp]
  tfidf_scores[col] = tfidf_scores[col]*weights[cat]

tfidf_scores['weighted_sum'] = tfidf_scores[lis].sum(axis=1)

tfidf_scores['content'] = list(df_subtag_article['content'])
tfidf_scores['webTitle'] = list(df_subtag_article['webTitle'])
tfidf_scores['vader_weighted_compound'] = list(df_subtag_article['vader_weighted_compound'])
tfidf_scores['link'] = list(df_subtag_article['link'])
tfidf_scores['keywords'] = list(df_subtag_article['keywords'])

final_results = tfidf_scores[(tfidf_scores['cosine_simi_no_weight']>=0.1) & (tfidf_scores['weighted_sum']>=0.1) & ((tfidf_scores['vader_weighted_compound']>0.1)|(tfidf_scores['vader_weighted_compound']<-0.1))]



