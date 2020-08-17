#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug 16 21:21:03 2020

@author: mark
"""


import pandas as pd
import matplotlib.pyplot as plt

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
