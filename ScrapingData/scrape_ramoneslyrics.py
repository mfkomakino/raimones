#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  5 17:53:44 2017


Scrape a Ramones Lyric Website and store in seperate and one combined file

@author: mfrey
"""


import requests
import re
from bs4 import BeautifulSoup
import time

#base_url = 'http://www.azlyrics.com/r/'
base_url = 'http://www.plyrics.com/'
page_html = '/r/ramones.html'

#headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0' }
headers = { 'User-Agent': 'Google Bot: Googlebot/2.1' }


base_dir = '/Users/mfrey/RamonesLyrics/'


#==============================================================================
# 
# Get URLS with Lyrics and album names: 
#==============================================================================

    
def get_parsed_page(url):
    """Return the content of the website on the given url in a parsed lxml format that is easy to query."""
    response = requests.get(url, headers=headers)
    parsed_page = BeautifulSoup(response.content, 'html.parser')
    return parsed_page



parsed_page = get_parsed_page(base_url+page_html)

#html = list(parsed_page.children)[2]
#body = list(html.children)[3]
#content = list(body.children)[13]

#song_albums = parsed_page.find(id="listAlbum")
#song_album2 = song_albums.find_all(class_="album")
#song_href = song_albums.find_all('href')

#song_album2.find_all(class_="album")

url_list_raw = list(parsed_page.find_all(href=re.compile("lyrics/ramones")))

url_list = []
for link in url_list_raw: 
    url_list.append( link.get('href'))


# Get list of albums: 
albums = list(parsed_page.find_all('div', class_='album_header'))
#print(parsed_page.find_all('div', style='text-align: left'))
album_list = []
for link in albums: 
    album_list.append( link.text.strip().replace("album: ",'').replace('"','').replace(' ','_').replace(':','()'))


#print(len(url_list))
##print(album_list)
#print(url_list)


#==============================================================================
#     Get the lyrics from the individual pages 
#==============================================================================
def get_lyrics(lyric_url):
    title = parsed_lyric_page('h3')[0].text
    #print(title)
    test = list(parsed_lyric_page.contents)[2]
    test2 = test.contents[3]#.contents[1].contents[3].contents[9]

    m = re.findall("<!-- start of lyrics -->.*?<!-- end of lyrics -->", str(test2), re.DOTALL)
    lyrics = m[0].replace('<!-- start of lyrics -->\r\n', '').replace('\n<!-- end of lyrics -->','').replace('<br/>','')
    return title, lyrics


# Write seperate files and collect all lyrics in one file: 

file_all = open(base_dir+'all_lyrics.txt','w')

for lyric_url in url_list:
    parsed_lyric_page = get_parsed_page(base_url+lyric_url)
    time.sleep(10) ## be kind with the websites... don't overload them and get blocked
    
    parsed_lyric_page = get_parsed_page(base_url+lyric_url)
    title, lyrics = get_lyrics(parsed_lyric_page)

    filename = lyric_url.replace('/lyrics/ramones/','').replace('.html','.txt')
    
    file = open(base_dir+filename,'w')    
    file.write(title+'\n\n')
    file.write(lyrics) 
    file_all.write(title+'\n\n')
    file_all.write(lyrics+'\n\n')
    file.close()

    
file_all.close()

print("done!")
