# LGBTQ_NYT
Natural Language Processing analysis of 50 years of L.G.B.T.Q articles. in the New York Times.
This analysis was conducted as Project 4 of my time at Metis. You can see the presentation in [NYT_LGBT.pdf](https://github.com/markafunke/rookiewr-regression/blob/master/preprocessing.py/). Ultimately found 9 distinct L.G.B.T.Q. topics from 1970-2020, with a clear change in prevalence over the years.

## Outline of Files

In order to re-produce the results of this linear regression model, clone this repository and run the code in the following order:

**1. scraper.py:** 

  - Leverages [NYT Article Search API](https://developer.nytimes.com/docs/articlesearch-product/1/overview) to pull 50 years worth of article metadata.
  *Note: you will need to acquire an API key for this code to run*
  - Uses results of API data pull to scrape article body text of ~12,000 articles and output into a dataframe

**2. preprocessing.py:** 

  - Cleans, tokenizes, and lemmatizes each scraped article for use in NLP unsupervised learning analysis in modeling.py

**3. modeling.py:** 

  - Topic modeling using Gensim LDA and Sklearn NMF, as well as sentiment analysis using TextBlob

**4. word_cloud.py:** 

  - Creates word clouds of results from NMF topic modeling in modeling.py
 
