#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Set of NLP logic that cleans, lemmatizes, and tokenizes dataframe of text

@author: markfunke
"""

import pandas as pd
import numpy as np
import re
import string
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk import pos_tag
from nltk.corpus import wordnet as wn
from collections import defaultdict

def clean_text(text):
    '''
    Removes punctuation, digits, and upper case from string of text

    Parameters
    ----------
    text : string
        string of text data

    Returns
    -------
    clean : string
        cleaned string of text

    '''  

    # Remove punctuation
    # NYT articles use curved versions of " and ', adding to punctiation list
    punctuation = string.punctuation + "“" + "‘" + "’" + "”"
    clean = re.sub('[%s]'%re.escape(punctuation), ' ', text)
    
    # Make all lowercase
    clean = clean.lower()
    
    # Retain HIV as a word. Punctuation removal loses this important word
    clean = clean.replace("h i v", "hivaids")
    
    # Remove digits
    clean = re.sub('\w*\d\w*', ' ', clean)
    return clean

if __name__ == __main__:
    
    article_df = pd.read_pickle("pickles/article_text.p")
    
    # Drop rows where we were not able to scrape the article text
    # This appears to happen often for very old articles where this is only a 
    # photo of the newspaper, or blog posts. About 5% in total.
    article_df.replace("", np.NaN, inplace=True)
    article_df.dropna(subset = ["article_text"], inplace=True)
    article_df.to_pickle("article_noNaNs.p")
    
    # Remove outlier article types like corrections, obituaries, lists etc.
    included_types = ["News", "Letter", "Op-Ed", "Editorial","Brief", "Archives"]
    mask = article_df.type_of_material.isin(included_types)
    article_df = article_df[mask]
    article_df.type_of_material.value_counts()
    article_df.decade.value_counts()
    
    # Limit to just article_text to move forward with NLP
    article_clean = article_df[["article_text"]]
    
    article_clean["article_text"] = article_clean["article_text"].apply(clean_text)
    article_clean.to_pickle("pickles/sentiment.p") # save file before lemmatize for sentiment
    
    #Tokenize
    article_clean["article_text"] = article_clean["article_text"].apply(word_tokenize)
    
    # Lemmatize all of Noun, Adjective, Verb, Adverb
    lemmatizer = WordNetLemmatizer()
    
    tag_map = defaultdict(lambda : wn.NOUN)
    tag_map['J'] = wn.ADJ
    tag_map['V'] = wn.VERB
    tag_map['R'] = wn.ADV
    
    article_clean['article_text'] = article_clean['article_text'].apply(
        lambda x: [lemmatizer.lemmatize(word, tag_map[tag[0]]) for word, tag in pos_tag(x)])
    article_clean['article_text'] = [' '.join(map(str, word)) for word in article_clean['article_text']]
    
    article_clean.to_pickle("cleaned_df.p")
