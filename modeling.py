#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug 23 11:45:44 2020

@author: markfunke
"""

import pandas as pd
import matplotlib.pyplot as plt
from gensim import models, matutils
from sklearn.decomposition import NMF
from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords

def LDA_topic_words(article_clean,stop_words_to_use,min_df=0,max_df=1,ngram_range=(1,1),
                    num_topics=2, passes = 10, alpha = 'auto', iterations = 1000):
    """
    Vectorizes documents, fits LDA model and returns doc-topic matrix
    
    Parameters
    ----------
    article_clean : DataFrame
        DataFrame containing "article_text" series which must be documents
        of text
    stop_words_to_use : Set
        stop words to be excluded from vectorizer
    min_df : sklearn TdidfVectorizer input, see documentation
        default is 0
    max_df : sklearn TdidfVectorizer input, see documentation
        default is 1
    ngram_range : sklearn TdidfVectorizer input, see documentation
        default is (1,1)
    num_topics : gensim LDA model input, see documentation
        default is 2
    passes : gensim LDA model input, see documentation
        default is 100
    alpha : gensim LDA model input, see documentation
        default is 'auto'
    iterations : gensim LDA model input, see documentation
        default is 1000

    Returns
    -------
    lda_docs : doc-topic matrix output from LDA

    """
    # Vectorize Text
    cv = TfidfVectorizer(min_df=min_df, max_df=max_df
                         ,ngram_range = ngram_range, stop_words = stop_words_to_use)
    cv.fit(article_clean["article_text"])
    doc_word = cv.transform(article_clean["article_text"]).transpose()
    
    # Convert sparse matrix of counts to a gensim corpus
    corpus = matutils.Sparse2Corpus(doc_word)
    id2word = dict((v, k) for k, v in cv.vocabulary_.items())
    
    # Create lda model    
    lda = models.LdaModel(corpus=corpus, num_topics=num_topics, id2word=id2word
                          ,passes=passes, alpha = alpha ,iterations=iterations)
    
    # Print topics and return doc-topic matrix
    lda.print_topics()
    lda_corpus = lda[corpus]
    lda_docs = [doc for doc in lda_corpus]  
    
    return lda_docs

def NMF_topic_words(article_clean,stop_words_to_use, n_topics=2, min_df=0, max_df=1, ngram_range = (1,1)):
    """

    Parameters
    ----------
    article_clean : DataFrame
        DataFrame containing "article_text" series which must be documents
        of text
    stop_words_to_use : Set
        stop words to be excluded from vectorizer
    n_topics : number of topics to output
        The default is 2.
    min_df : sklearn TdidfVectorizer input, see documentation
        default is 0
    max_df : sklearn TdidfVectorizer input, see documentation
        default is 1
    ngram_range : sklearn TdidfVectorizer input, see documentation
        default is (1,1)

    Returns
    -------
    doc_topic : doc-topic matrix output from NMF
    topic_word : topic-word matrix output from NMF

    """
    
    # Vectorize text
    cv = TfidfVectorizer(min_df=min_df, max_df=max_df, ngram_range = ngram_range, stop_words = stop_words_to_use)
    cv.fit(article_clean["article_text"])
    doc_word = cv.transform(article_clean["article_text"])
    
    # Fit NMF model
    nmf_model = NMF(n_topics)
    doc_topic = nmf_model.fit_transform(doc_word)
    
    # Create topic-word matrix and print top words for each topic
    columns = ["topic"+str(n) for n in range(n_topics)]
    topic_word = (pd.DataFrame(nmf_model.components_.round(3),
             index = columns,
             columns = cv.get_feature_names()).transpose())
    for n in range(n_topics):
        topic_words = topic_word.sort_values(by=columns[n], ascending=False).iloc[0:15,n]
        print(topic_words)
        
    return doc_topic, topic_word
        
def find_bins(year,low_end,high_end,width):
    """
    Places year into pre-defined bins as described by user
    
    low_end: low range of year bins
    high_end: high range of year bins
    width: interval of year bins
    """
    bins = list(range(low_end,high_end+width*2,width))
    for i, num in enumerate(bins):
        if year < num:
            return bins[i-1]
        
def sentiment_analysis(sent_df):
    """
    Performs TextBlob sentiment analysis on DataFrame of documents
    
    Parameters
    ----------
    sent_df : DataFrame
        DataFrame containing text documents to be evaluated

    Returns
    -------
    sent_df : DataFrame
        Contains document, polarity, and sentiment score

    """
    pol = []
    sub=[]
    for article in sent_df.article_text:
        sentp = TextBlob(article).sentiment.polarity
        sents = TextBlob(article).sentiment.subjectivity
        pol.append(sentp)
        sub.append(sents)  
       
    sent_df['Polarity'] = pol
    sent_df['Subjectivity'] = sub
    return sent_df

if __name__ == __main__:
    
    # Read in article_clean from preprocessing.py
    article_clean = pd.read_pickle("pickles/cleaned_df.p")
    
    # Create stop word list
    # Import csv created from stopword collection at the following site:
    # https://www.ranks.nl/stopwords
    stop_words_csv = pd.read_csv("csv/stopwords.csv")
    stop_word_list = [word for word in stop_words_csv.stop_words]
    stop_word_list.extend(stopwords.words('english')) # Add NLTK stopword list
    # manually added stopwords related to topics
    stop_word_list.extend(["gay", "homosexual", "lesbian", "men", "woman", "york"
                           ,"homosexuality", "editor", "article", "news", "year"
                           ,"book", "guy", "girl", "man"])
    stop_words_to_use = set(stop_word_list)
    
    # Fit LDA model
    # Note: This is an iterative process and can be used to test multiple
    # parameters to find the best topic outputs
    # Ultimately found LDA did not work well for finding intelligib topics
    lda_docs = \
    LDA_topic_words(article_clean,stop_words_to_use,min_df=0.01,max_df=.9,ngram_range=(1,2)
    ,num_topics=5, passes = 100, alpha = 'auto', iterations = 5000)
    
    # Find most likely topic for each document
    max_topics = []
    for doc in lda_docs:
        max_topic =  max(doc,key=lambda item:item[1])[0]
        max_topics.append(max_topic)
    
    article_topics = pd.read_pickle("pickles/article_noNaNs.p").reset_index()
    article_topics["max_topic"] = pd.Series(max_topics)
    article_topics.max_topic.value_counts()
    
    # Evaluate topic distribution by decade
    article_topics.groupby(['decade','max_topic']).size().unstack(fill_value=0)
    
    # Note: This is an iterative process and can be used to test multiple
    # parameters to find the best topic outputs
    # The model shown below is the iteration that found the best topics,
    # in my qualitative, subjective opinion 
    doc_topic, topic_word = NMF_topic_words(article_clean, stop_words_to_use
                        ,n_topics= 9, min_df=0.01, max_df=.9, ngram_range = (1,2))
    
    # Save for word_cloud creation
    topic_word.to_pickle("pickles/topic_words.p")
    
    # Create Output For Tableau Modeling
    doc_topic['Max'] = doc_topic.idxmax(axis=1)
    
    summary = pd.read_pickle("pickles/article_noNaNs.p").reset_index()
    summary["topic"] = doc_topic['Max']
    
    summary["year"] = summary["year"].astype(int)
    summary["year_bin"] = summary["year"].apply(find_bins,low_end=1960,high_end=2020,width=5)
    chart = summary.groupby(['year','topic']).size().unstack(fill_value=0) # quick view of distribution
    
    tableau = summary.loc[summary['year']>1969,["year","year_bin","decade","topic"]]
    topic_dict = {0:"Love/Relationships",1:"Marriage",2:"Religion",3:"Military"
                  ,4:"Politics",5:"Parade/March/Crime",6:"HIV/AIDS",7:"Gender Identity"
                  ,8:"Boy Scouts"}
    tableau["topic_name"] = tableau["topic"].apply(lambda x: topic_dict[x])    
    tableau.to_csv("csv/tableau_topics.csv")
    
    #Sentiment Analysis
    sent_df = pd.read_pickle("pickles/sentiment.p").reset_index()
    
    sent_df = sentiment_analysis(sent_df)
    sent_df.reset_index(inplace=True)
    sent_df["year"] = summary["year"]
    sent_df["decade"] = summary["decade"]
    sent_df["year_bin"] = summary["year_bin"]
    sent_df["topic"] = summary["topic"]
    
    pol_year = sent_df.groupby(['year']).Polarity.mean()
    pol_year_bin = sent_df.groupby(['year_bin']).Polarity.mean()
    pol_decade = sent_df.groupby(['decade']).Polarity.mean()
    pol_topic = sent_df.groupby(['topic']).Polarity.mean()
    
    plt.hist(sent_df[sent_df.topic == 0].Polarity,bins=20,range=[-.5, .5]);
    plt.hist(sent_df[sent_df.topic != 0].Polarity,bins=20,range=[-.5, .5]);
    
    plt.plot(pol_topic)