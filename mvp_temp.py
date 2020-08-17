#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug 16 21:21:03 2020

@author: mark
"""


import pandas as pd
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup

article_df = pd.read_pickle("articles.p")

article_df["year"] = article_df["date"].apply(lambda x: x[0:4])
article_df["decade"] = article_df["year"].apply(lambda x: int(x[0:3] + "0"))

article_df["abstract_word_count"] = article_df["abstract"].apply(lambda x: len(x))
article_df["lead_word_count"] = article_df["lead_paragraph"].apply(lambda x: len(x))

article_df.decade.value_counts()

plt.figure(figsize=(10,10))
plt.hist(article_df.decade)
ply.xlim(1955,2025);


article_df.to_csv("articles.csv")

article_df.abstract


# test beautiful soupys

<p class="css-158dogj evys1bk0">Where do the new faces actually come from? Ryan Laney, France’s visual effects supervisor and a 30-year veteran whose credits include “Harry Potter and the Chamber of Secrets” (2002), persuaded the director that a deep-learning computer process was the easiest answer, even on a documentary’s tight budget. For “Welcome to Chechnya,” he set up a secret editing suite and remained entirely offline while on the job.</p>

article_df_scrape = article_df.reset_index()

article_text = []
i = 0
for url in article_df_scrape.web_url[0:101]:
    article_text.append(scrape_article_text(url))
    i += 1
    if i % 100 == 0:
        time.sleep(10) # sleep 10 seconds every 100 articles
    else:
        time.sleep(0.5) # sleep half second every other time
        
article_df_scrape["article_text"] = article_text
article_df_scrape.to_pickle("article_text.p")   
    

def scrape_article_text(web_url):
    try:
        url = web_url
    
        response = requests.get(url)
               
        page = response.text
        soup = BeautifulSoup(page, "lxml")
        
        # find all paragraphs in article, and store as one block of text
        article_text = ' '.join([p.text for p in soup.find_all("p", {'class':'css-158dogj evys1bk0'})])
    except:
        article_text = ""
    
    return article_text
            
