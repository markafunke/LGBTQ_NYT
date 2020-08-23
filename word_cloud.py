#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Creates wordclouds for topic modeling 

@author: markfunke
"""

import pandas as pd
from PIL import Image
import numpy as np
from wordcloud import WordCloud, ImageColorGenerator
from palettable.colorbrewer.diverging import Spectral_9
from matplotlib.colors import makeMappingArray
import matplotlib.pyplot as plt

# Create Word Cloud for topics
def create_word_cloud(topic_word,topic_num,mask,num_words,file_name):
    """

    Parameters
    ----------
    topic_word : DataFrame 
        topic-word  matrix output
    topic_num : integer
        topic column in matrix to create word cloud
    mask : array
        image array to fit word cloud shape
    num_words : integer
        number of words to include in word cloud
    file_name : string
        path of filename to save

    Returns
    -------
    None. Saves wordcloud file.

    """
    topic_words = topic_word.sort_values(by=columns[topic_num], ascending=False).iloc[0:num_words,topic_num].reset_index()
    word_dict = dict(zip(topic_words.iloc[:,0], topic_words.iloc[:,1]))
    
    # manual edits to clean up certain words
    if topic_num == 6:
        word_dict["AIDS"] = word_dict.pop("aid")
        word_dict["HIV"] = word_dict.pop("hivaids")
        word_dict["doctor"] = word_dict.pop("dr")
    
    wc = WordCloud(font_path=font_path, width=3000, height=2000, mode = "RGBA",color_func=lambda *args, **kwargs: "black", background_color=None,collocations=True, mask=mask).generate_from_frequencies(word_dict)
    
    plt.figure( figsize=(20,10), facecolor='k')
    plt.imshow(wc)
    plt.axis("off")
    plt.tight_layout(pad=0)
    plt.show()
    wc.to_file(f"images/word_clouds/{file_name}.png")
    
def gradient_cloud(cloud_dict, icon_path, font_path, gradient_orientation, output_path):
    """

    Parameters
    ----------
    cloud_dict : dictionary
        DESCRIPTION.
    icon_path : string
        path to icon to use for wordcloud shape
    font_path : string
        path to font to use for wordcloud
    gradient_orientation : string
        "vertical" for vertical gradient, else horizonatal
    output_path : string
        path of filename to save

    Returns
    -------
    None.

    """

    # Leveraged public github repo code from Max Woolf
    # https://github.com/minimaxir/stylistic-word-clouds/blob/master/wordcloud_cnn_reactions.py
    # Edited slightly to make into a function
    icon = Image.open(icon_path).convert("RGBA")
    mask = Image.new("RGBA", icon.size, (255,255,255))
    mask.paste(icon,icon)
    mask_wordcloud = np.array(mask)
    
    # Create a linear gradient using the matplotlib color map
    imgsize = icon.size
    palette = makeMappingArray(imgsize[1], Spectral_9.mpl_colormap)   # interpolates colors
    
    for y in range(imgsize[1]):
        for x in range(imgsize[0]):
        	if mask.getpixel((x,y)) != (255,255,255):   # Only change nonwhite pixels of icon
        	
        		color = palette[y] if gradient_orientation == "vertical" else palette[x]
        		
        		# matplotlib color maps are from range of (0,1). Convert to RGB.
        		r = int(color[0] * 255)
        		g = int(color[1] * 255)
        		b = int(color[2] * 255)
        		
        		mask.putpixel((x, y), (r, g, b))
    			
    # create coloring from image
    image_colors = ImageColorGenerator(np.array(mask))
   
    # generate word cloud     
    wc = WordCloud(font_path=font_path, background_color="black", max_words=2000, mask=mask_wordcloud,
                   max_font_size=400, random_state=42)
                   
    wc.generate_from_frequencies(cloud_dict)
    wc.recolor(color_func=image_colors)
    wc.to_file(output_path)

if __name__ == __main__:
    
    # Read in final topic-word matrix from NMF results in modeling.py
    topic_word = pd.read_pickle("pickles/topic_words.p")
    
    # Convert image to arrays for masks in wordcloud
    rainbow_mask = np.array(Image.open('images/rainbow.jpg'))
    
    # Create clouds for each topic
    create_word_cloud(topic_word,0,rainbow_mask,40,"love")
    create_word_cloud(topic_word,1,rainbow_mask,40,"marriage")
    create_word_cloud(topic_word,2,rainbow_mask,40,"religion")
    create_word_cloud(topic_word,3,rainbow_mask,40,"military")
    create_word_cloud(topic_word,4,rainbow_mask,40,"politics")
    create_word_cloud(topic_word,5,rainbow_mask,40,"parade")
    create_word_cloud(topic_word,6,rainbow_mask,40,"HIV")
    create_word_cloud(topic_word,7,rainbow_mask,40,"gender")
    create_word_cloud(topic_word,8,rainbow_mask,40,"scouts")
    
    # Create title slide with words from all topics overlayed on a pride flag
    # and the title "LGBTQ in the New York Times"
    
    # Create dictionary of words
    cloud_df = topic_word.copy()
    cloud_df["value"] = topic_word.max(axis=1)
    cloud_df.reset_index(inplace=True)
    cloud_dict = dict(zip(cloud_df.iloc[:,0], cloud_df.iloc[:,-1]))
    
    # Add Title Words as the largest frequency
    cloud_dict["LGBTQ in the New York Times"] = 30
    
    # Nitpicky edits to clean up image
    cloud_dict["AIDS"] = cloud_dict.pop("aid")
    cloud_dict["HIV"] = cloud_dict.pop("hivaids")
    cloud_dict["doctor"] = cloud_dict.pop("dr")
    cloud_dict["AIDS"] = 2.4
    cloud_dict["civil union"] = 2.4
    cloud_dict["supreme court"] = 2.4
    cloud_dict["love"] = 2
    
    # Generate gradient cloud
    font_path = "font/AmaticSC-Bold.ttf"
    gradient_orientation = "horizontal"
    icon_path = 'images/rainbow.jpg'
    output_path = "images/flag_title.png"
    gradient_cloud(cloud_dict, icon_path, font_path, gradient_orientation, output_path)
