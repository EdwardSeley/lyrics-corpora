
# coding: utf-8

# In[3]:


#!/usr/bin/env python3


# In[4]:


"""
Get lyrics from your favorite songs, artists, genres, and billboard charts! This is a WikiaLyrics API, 
but distinguishes itself from others like it (eg. lyric-api) because it searches for the artist and song through 
the lyrics.wikia.com website, thereby allowing for variations in the song or artist's name.
"""


# In[19]:


import billboard
import requests
from bs4 import BeautifulSoup
import argparse


# In[21]:


GENRE_LIST = ["r-b-hip-hop", "country", "rock", "latin", "dance-electronic", "christian", "gospel"]
SEARCH_URL = "http://lyrics.wikia.com/wiki/Special:Search?search={}:{}"
BASE_URL = "http://lyrics.wikia.com/wiki/{}"
MAIN_ARTIST_CUT_OFFS = [" Featuring", " x ", " X ", " Duet With ", " &", ","] #finds artist name by extracting string before cutoff


# In[18]:


def getLyrics(artist, title):
    try:
        url = SEARCH_URL.format(artist.replace(" ", "+"), title.replace(" ", "+"))
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
    music_collection = dict({})
    while (weekNum < totalWeeks):
        while (songIndex < len(chart.entries)):
            song = chart[songIndex]
            artist = song.artist
            for cut_off in MAIN_ARTIST_CUT_OFFS:
                if cut_off in artist:
                    artist = artist[:artist.find(cut_off)]
            title = song.title
            lyrics = None
            if artist not in music_collection:
                music_collection[artist] = {}
            if title not in music_collection[artist]:
                lyrics = getLyrics(song.artist, title)
                if lyrics is None:
                    lyrics = getLyrics(artist, title)
                music_collection[artist][title] = lyrics
                if lyrics is None:
                    music_collection[artist][title] = ""
            songIndex += 1
        weekNum += 1
        songIndex = 0
        chart = billboard.ChartData('hot-100', chart.previousDate)
    return music_collection


# In[6]:


def getGenreCorpus(genre):
    if genre not in getGenreList():
        raise Exception('genre, {0} is not in the accepted genre list. Please use getGenreList() to find acceptable genres. '.format(genre))
    chart = billboard.ChartData('{0}-songs'.format(genre))
    return getBillboardCorpus(104, chart)


# In[7]:


def getArtistCorpus(artist):
    artistCorpus = {}
    for album in getAlbumListFromArtist(artist):
        artistCorpus[album[0]] = {}
        for song in getSongListFromAlbum(album):
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


def getAlbumListFromArtist(artist):
    page = requests.get(BASE_URL.format(artist))
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


def getSongListFromAlbum(album):
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
    


# In[20]:


def corpusToString(corpus):
    lyrics = ""
    for x in corpus.keys():
        for y in corpus[x]:
            lyrics += corpus[x][y]
    return lyrics


# In[17]:


def main():
    parser = argparse.ArgumentParser(description="Get lyrics from your favorite songs, artists, genres, and billboard charts!")
    
    parser.add_argument(
    "-a", "--artist",
    help="Specify the artist's name",
    required=False
    )
    parser.add_argument(
    "-t", "--title",
    help="Specify the song's title",
    required=False
    )
    parser.add_argument(
    "-g", "--genre",
    help="Specify the genre of lyrics you would like to receive",
    required=False
    )
    parser.add_argument(
    "-gl", "--genrelist",
    help="Returns a list of the genres from which you can retrieve a corpus of lyrics",
    required=False,
    action='store_true'
    )
    parser.add_argument(
    "-b", "--billboardchart",
    help="Specify the number of weeks for the billboard charts",
    required=False
    )
    
    args = parser.parse_args()
    
    if args.artist:
        if args.title:
            print(getLyrics(args.artist, args.title))
        else:
            print(corpusToString(getArtistCorpus(args.artist)))
    elif args.genre:
        print(corpusToString(getGenreCorpus(args.genre)))
    elif args.genrelist:
        print(getGenreList())
    elif args.billboardchart:
        print(corpusToString(getBillboardCorpus(args.billboardchart)))
    else:
        raise Exception("An argument, such as -a artist -t title, is needed")


# In[14]:


if __name__ == '__main__':
    main()

