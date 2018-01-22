
# coding: utf-8

# In[43]:


import billboard
import requests
from bs4 import BeautifulSoup
import nltk
from nltk import word_tokenize
from nltk.util import ngrams
from nltk.corpus import wordnet as wn
import random


# In[3]:


def getLyricsFromWikia(artist, title):
    try:
        BASE_URL = "http://lyrics.wikia.com/wiki/Special:Search?search={}:{}"
        url = BASE_URL.format(artist.replace(" ", "+"), title.replace(" ", "+"))
        page = requests.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')
        resultBox = soup.find("li", {'class', 'result'})
        resultLink = resultBox.find("a", {'class', 'result-link'}, href=True)
        resultUrl = resultLink.get('href')
        page = requests.get(resultUrl)
        soup = BeautifulSoup(page.text, 'html.parser')
        lyricBox = soup.find('div', {'class': 'lyricbox'})
        for br in lyricBox.findAll('br'):
            br.replace_with('\n')
        return lyricBox.text.strip()
    except:
        return None


# In[4]:


def getBillboardCorpus(totalWeeks=1, chart=billboard.ChartData('hot-100')):
    songIndex = 0
    weekNum = 0
    cut_off_list = [" Featuring", " x ", " X ", " Duet With ", " &", ","]
    music_collection = dict({})
    while (weekNum < totalWeeks):
        while (songIndex < len(chart.entries)):
            song = chart[songIndex]
            artist = song.artist
            for cut_off in cut_off_list:
                if cut_off in artist:
                    artist = artist[:artist.find(cut_off)]
            title = song.title
            lyrics = None
            if artist not in music_collection:
                music_collection[artist] = {}
            if title not in music_collection[artist]:
                lyrics = getLyricsFromWikia(song.artist, title)
                if lyrics is None:
                    lyrics = getLyricsFromWikia(artist, title)
                music_collection[artist][title] = lyrics
                if lyrics is None:
                    music_collection[artist][title] = ""
            songIndex += 1
        weekNum += 1
        songIndex = 0
        chart = billboard.ChartData('hot-100', chart.previousDate)
    return music_collection


# In[5]:


def getGenreList():
    return ["r-b-hip-hop", "country", "rock", "latin", "dance-electronic", "christian", "gospel"]


# In[6]:


def getGenreCorpus(genre):
    if genre not in getGenreList():
        raise Exception('genre, {0} is not in the accepted genre list. Please use getGenreList() to find acceptable genres. '.format(genre))
    chart = billboard.ChartData('{0}-songs'.format(genre))
    return getBillboardCorpus(104, chart)


# In[7]:


def getArtistCorpus(artist):
    artistCorpus = {}
    for album in getAlbums(artist):
        artistCorpus[album[0]] = {}
        for song in getSongs(album):
            try:
                page = requests.get(song[1])
                soup = BeautifulSoup(page.content, 'html.parser')
                lyricBox = soup.find('div', {'class': 'lyricbox'})
                for br in lyricBox.findAll('br'):
                    br.replace_with('\n')
                lyrics = lyricBox.text.strip()
                artistCorpus[album[0]][song[0]] = lyrics
            except:
                continue
    return artistCorpus


# In[8]:


def getAlbums(artist):
    BASE_URL = "http://lyrics.wikia.com/wiki/{}".format(artist)
    page = requests.get(BASE_URL)
    soup = BeautifulSoup(page.content, "html.parser")
    headlines = soup.findAll("span", {"class", "mw-headline"})
    albums = []
    for headline in headlines:
        link = headline.find("a")
        if link is not None:
            title = link["title"]
            albumTitle = title[title.find(":")+1:title.find(" (")]
            albums.append( (albumTitle, "https://lyrics.wikia.com{0}".format(link["href"])))
    return albums


# In[9]:


def getSongs(album):
    link = album[1]
    page = requests.get(link)
    soup = BeautifulSoup(page.content, "html.parser")
    content = soup.find("div", {"class":"mw-content-text"})
    songs = []
    if content is not None:
        trackListBox = content.find("ol")
        songItems = trackListBox.findAll("li")
        for songItem in songItems:
            songLink = songItem.find("a")
            title = songLink.string
            url = "http://lyrics.wikia.com{0}".format(songLink["href"])
            songs.append((title, url))
    return songs
    


# In[10]:


def corpusToString(corpus):
    lyrics = ""
    for album in corpus.keys():
        for song in corpus[album]:
            lyrics += corpus[album][song]
    return lyrics


# In[11]:


def save(lyrics, name):
    with open("{}Text.txt".format(name), "w", encoding='utf-8') as file:
        file.write(lyrics)


# In[12]:


def retrieve(nameOfArtist):
    with open("{}Text.txt".format(nameOfArtist), "r") as file:
        lyrics = file.read()
    return lyrics


# In[13]:


def process(lyrics):
    tokens = word_tokenize(lyrics)
    text = nltk.Text(tokens)
    return text


# In[2]:


def keyWords(corpus):
    fdist = nltk.FreqDist(corpus)
    stopWords = nltk.corpus.stopwords.words("english")
    keyWords = [keyWord for keyWord in set(corpus) if fdist[keyWord] > 25 and len(keyWord) > 5 and keyWord not in stopWords] #targets frequent words and filters out articles
    return keyWords

