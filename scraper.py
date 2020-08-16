#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 13 18:49:26 2020

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

api_key = "RATeD96Ims1OhrnqBKNJ0juy50xOyDWO"

dates = pd.DataFrame(pd.date_range(start='1/1/1960', periods=3162, freq='W'),columns=["date_begin"])
dates["date_end"] = dates.date_begin + datetime.timedelta(days=6)

date_begin = [int(str(x.year)+str(x.month).zfill(2)+str(x.day).zfill(2)) for x in dates.date_begin]
date_end = [int(str(x.year)+str(x.month).zfill(2)+str(x.day).zfill(2)) for x in dates.date_end]

dates = tuple(zip(date_begin,date_end))

i = 0
article_df_all = pd.DataFrame()
for date in dates:
    begin_date = date[0]
    end_date = date[1]
    print(f"scraping {i} / {len(dates)}")
    articles = scrape_nyt_lgbtq(begin_date, end_date, api_key)
    time.sleep(6) #NYT API allows 10 requests per minute (1 every 6 seconds)
    article_dic = parse_api(articles)
    article_df =  pd.DataFrame(article_dic)
    article_df_all = pd.concat([article_df,article_df_all],axis=0)
    i += 1
article_df_all.to_pickle("articles.p")
article_test_pick = pd.read_pickle("articles.p")

# def scrape_nyt_lgbtq(begin_date, end_date, api_key):
#   requestUrl = f"https://api.nytimes.com/svc/search/v2/articlesearch.json?begin_date={begin_date}&end_date={end_date}&fq=subject%3A%20%22Homosexuality%22&api-key={api_key}"
#   requestHeaders = {
#     "Accept": "application/json"
#   }

#   request = requests.get(requestUrl, headers=requestHeaders)

#   return request.json()


def scrape_nyt_lgbtq(begin_date, end_date, api_key):
  requestUrl = f"https://api.nytimes.com/svc/search/v2/articlesearch.json?begin_date={begin_date}&end_date={end_date}&fq=subject%3A(%22homosexuality%22%2C%22homosexuality%20and%20bisexuality%22%2C%22same-sex%20marriages%2C%20civil%20unions%20and%20domestic%20partnerships%22%2C%22transgender%20and%20transsexuals%22)&api-key={api_key}"
  requestHeaders = {
    "Accept": "application/json"
  }

  request = requests.get(requestUrl, headers=requestHeaders)

  return request.json()



def parse_api(articles):
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


# def scrape_nyt_lgbt(min_year, max_year):
#     """
#      Parameters
#      ----------
#      n_pages : Integer, optional
#          Amount of pages to scrape, 10 results per page. The default is 1.
    
#      Returns
#      -------
#     article_df : DataFrame
#          DataFrame containing one article per row with
#          link to article, article header, and article preview
#     """

#     # Use selennium to open LGBTQ topic page
#     url = "https://www.nytimes.com/topic/subject/homosexuality"
    
#     chromedriver = "/Applications/chromedriver" 
#     os.environ["webdriver.chrome.driver"] = chromedriver
#     driver = webdriver.Chrome(chromedriver)
#     driver.get(url)
    
#     # Instantiate dictionary and counter(i)
#     article_dict = {}
#     i = 0
#     time.sleep(5)
    
#     # Scrape url, headline, and preview for every year/month combination
#     for year in range(min_year,max_year+1):
    
#         for month in ["january","february","march","april","may","june","july","august","september","october","november","december"]:
#             # search month by month to retrieve articles as each page can only display
#             # a max of 100 articles, even after clicking "Show More"
#             search_box = driver.find_element_by_xpath("//input[@id='search-tab-input']")
#             search_box.click() # activate search box
#             search_box.clear() #clear the current search
#             search_box.send_keys(f"{month} {year}") #input new search
#             # search_box.send_keys(Keys.RETURN) #hit enter
#             print(f"{month} {year}")
#             time.sleep(1)
        
#             # Click "Show More" Button to view 10 more articles
#             # Try clicking up to 10 times, pages max out at 100 articles
#             # Most months won't require many clicks, so adding a try/except
#             # to continue if "Show More" button isn't there anymore
#             for n in range(10):
#                 try:
#                     show_more_button = driver.find_elements_by_xpath("//button[@type='button' and @aria-pressed='false']")[0]
#                     show_more_button.click()
#                     time.sleep(1) # sleep after every page to not get banned
#                     # print(f"Pressing button on page {n}")
#                 except:
#                     continue
             
#             # Scrape all articles that are now loaded onto the page
#             soup = BeautifulSoup(driver.page_source)
            
#             try:
#                 article_divs = [item for item in soup.find_all("div", {"class": "css-1l4spti"})]
#                 for item in article_divs:
#                     link = item.a['href']
#                     header = item.find("h2", {"class": "css-1j9dxys e1xfvim30"}).text
#                     preview = item.p.text
#                     article_dict[i] = [link,header,preview]
#                     i += 1
#             except:
#                 # if logic doesn't work, it is likely not an article,
#                 # but a slideshow or video, just leaving inputs blank
#                 # to see how often this happens. Can remove later
#                 article_dict[i] = []
            
#     # convert dictionary of every article into dataframe
#     # drop duplicates -- some articles will show up under multiple dates
#     # the search returns articles published in that month, but also articles
#     # whose date is mentioned in the body of the article 
#     article_df = pd.DataFrame(article_dict).T
#     article_df.columns= (["link","header","preview"])
#     article_df.drop_duplicates(subset="header", inplace=True)
    
#     return article_df


# articles = scrape_nyt_lgbt(1960,2020)
# articles["year"] = articles["link"].apply(lambda x: x[1:5])
# articles.year.value_counts()

# articles.to_pickle("articles.p")

