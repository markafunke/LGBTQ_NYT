#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Set of functions to pull LGBTQ articles from NYT API, and scrape article text
Creates a dataframe with API and Article Text

@author: mark
"""

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
import requests
import numpy as np
import re
import time
import os
import datetime

def nyt_lgbtq_api(begin_date, end_date, api_key):
    """
    Pulls .json output for date range 
    from NYT Article Search API, specific to the LGBTQ topic
    
    Parameters
    ----------
    begin_date : str
        10 digit string of lower end of date range to access (YYYYMMDD)
    end_date : str
        10 digit string of higher end of date range to access (YYYYMMDD)
    api_key : str
        api key from NYT, approved to access Article Search API

    Returns
    -------
    .json
        json output of all articles in that date range

    """
    requestUrl = f"https://api.nytimes.com/svc/search/v2/articlesearch.json?begin_date={begin_date}&end_date={end_date}&fq=subject%3A(%22homosexuality%22%2C%22homosexuality%20and%20bisexuality%22%2C%22same-sex%20marriages%2C%20civil%20unions%20and%20domestic%20partnerships%22%2C%22transgender%20and%20transsexuals%22)&api-key={api_key}"
    requestHeaders = {
      "Accept": "application/json"
    }
    
    request = requests.get(requestUrl, headers=requestHeaders)
    
    return request.json()

def parse_api(articles):
    """
    Parses json output of articles returned from NYT Article Search API
    into a dictionary with a key for each article

    Parameters
    ----------
    articles : json output from Article Search API

    Returns
    -------
    news : dictionary
        key for each article, values shown in "items_to_parse"

    """
    items_to_parse = ['_id','abstract','lead_paragraph','snippet','section_name','word_count','type_of_material','news_desk','web_url']
    news = []
    for i in articles['response']['docs']:
        dic = {}
        for item in items_to_parse:
            try:
                dic[item] = i[item]
            except:
                dic[item] = ""
                
        # other items not as straightforward to parse
        dic['headline'] = i['headline']['main']
        dic['date'] = i['pub_date'][0:10] # just want year/mo/day, not time
    
        # there are multiple keywords listed for both subjects and locations, storing all of them
        locations = []
        for x in range(0,len(i['keywords'])):
            if 'glocations' in i['keywords'][x]['name']:
                locations.append(i['keywords'][x]['value'])
        dic['locations'] = locations
        subjects = []
        for x in range(0,len(i['keywords'])):
            if 'subject' in i['keywords'][x]['name']:
                subjects.append(i['keywords'][x]['value'])
        dic['subjects'] = subjects
    
        news.append(dic)
    return news

def scrape_article_text(web_url):
    """
    Scrapes article body text for a given New York Times url

    Parameters
    ----------
    web_url : string
        URL pointing to New York Times article page

    Returns
    -------
    article_text : string
        Article body text

    """
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


if __name__ == __main__:
    
    # API Key for article_search API on New York Times
    api_key = "YOUR_API_KEY_HERE"
    
    # Create list of every week from 1960 to 2020
    # This is used as an input into the NYT API
    dates = pd.DataFrame(pd.date_range(start='1/1/1960', periods=3162, freq='W'),columns=["date_begin"])
    dates["date_end"] = dates.date_begin + datetime.timedelta(days=6)
    date_begin = [int(str(x.year)+str(x.month).zfill(2)+str(x.day).zfill(2)) for x in dates.date_begin]
    date_end = [int(str(x.year)+str(x.month).zfill(2)+str(x.day).zfill(2)) for x in dates.date_end]
    dates = tuple(zip(date_begin,date_end))
    
    # Parse article data from 1960 to 2020 from NYT Article Search API
    i = 0
    article_df_all = pd.DataFrame()
    for date in dates:
        begin_date = date[0]
        end_date = date[1]
        print(f"scraping {i} / {len(dates)}")
        articles = nyt_lgbtq_api(begin_date, end_date, api_key)
        time.sleep(6) #NYT API allows 10 requests per minute (1 every 6 seconds)
        article_dic = parse_api(articles)
        article_df =  pd.DataFrame(article_dic)
        article_df_all = pd.concat([article_df,article_df_all],axis=0)
        i += 1
       
    # Save pickle as checkpoint after API runs
    article_df_all.to_pickle("pickles/articles.p").
    article_df = pd.read_pickle("pickles/articles.p")
    
    # Create year, decade, and word_count columns
    article_df["year"] = article_df["date"].apply(lambda x: x[0:4])
    article_df["decade"] = article_df["year"].apply(lambda x: int(x[0:3] + "0"))
    article_df["abstract_word_count"] = article_df["abstract"].apply(lambda x: len(x))
    article_df["lead_word_count"] = article_df["lead_paragraph"].apply(lambda x: len(x))
    
    # Scrape actual article text for every url in dataframe
    article_df_scrape = article_df.reset_index()
    article_text = []
    i = 0
    for url in article_df_scrape.web_url:
        article_text.append(scrape_article_text(url))
        i += 1
        print(f"scraping article {i}")
        if i % 100 == 0:
            time.sleep(10) # sleep 10 seconds every 100 articles
        else:
            time.sleep(0.5) # sleep half second every other time
    
    # Save final dataframe with article text for use in rest of analysis        
    article_df_scrape.to_pickle("pickles/article_text.p")   


