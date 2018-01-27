
# coding: utf-8

# In[255]:


#!/usr/bin/env python3


# In[256]:


"""
Get lyrics from your favorite songs, artists, genres, and billboard charts! This is a WikiaLyrics API, 
but distinguishes itself from others like it (eg. lyric-api) because it searches for the artist and song through 
the lyrics.wikia.com website, thereby allowing for variations in the song or artist's name.
"""


# In[257]:


import billboard
import requests
from bs4 import BeautifulSoup
import argparse


# In[258]:


GENRE_LIST = ["r-b-hip-hop", "country", "rock", "latin", "dance-electronic", "christian", "gospel"]
SEARCH_URL = "http://lyrics.wikia.com/wiki/Special:Search?search={0}:{1}"
BASE_URL = "http://lyrics.wikia.com/{0}"
MAIN_ARTIST_CUT_OFFS = [" Featuring", " x ", " X ", " Duet With ", " &", ","] #finds artist name by extracting string before cutoff


# In[259]:


class Artist:
    
    def __init__(self, name):
        self.name = name
        self.albumList = None
    
    def getName(self):
        return self.name
    
    def getAlbumList(self):
        if self.albumList is None:
            page = requests.get(BASE_URL.format(artist.getName()))
            soup = BeautifulSoup(page.content, "html.parser")
            headlines = soup.findAll("span", {"class", "mw-headline"})
            albumList = []
            for headline in headlines:
                link = headline.find("a")
                if link is not None:
                    title = link["title"]
                    albumTitle = title[title.find(":")+1:title.find(" (")]
                    album = Album(albumTitle, artist, BASE_URL.format(link["href"]))
                    albumList.append(album)
            self.albumList = albumList
        return self.albumList
    
    def getSongList(self):
        return [song for album in self.getAlbumList() for song in album.getSongList()]
    
    def getLyrics(self):
        lyrics = ""
        for album in self.getAlbumList():
            for song in album.getSongList():
                try:
                    if song.lyrics is None:
                        page = requests.get(song.getLink())
                        soup = BeautifulSoup(page.content, 'html.parser')
                        lyricBox = soup.find('div', {'class': 'lyricbox'})
                        for br in lyricBox.findAll('br'):
                            br.replace_with('\n')
                        songLyrics = lyricBox.text.strip()
                        lyrics += songLyrics
                        song.setLyrics(songLyrics)
                    else:
                        lyrics += song.getLyrics()
                except:
                    continue
        return lyrics
    
    def __str__(self):
        return self.name
    
    def __repr__(self):
        return str(self)
    
    def __eq__(self, other): 
        return self.name == other.name
    
    def __hash__(self):
        return hash(self.name)


# In[260]:


class Album:
    
    def __init__(self, name, artist, link=None):
        self.name = name
        self.artist = artist
        self.link = link
        self.songList = []
            
    def getArtist(self):
        return self.artist
    
    def getSongList(self):
        if not self.songList:
            link = self.getLink()
            page = requests.get(link)
            soup = BeautifulSoup(page.content, "html.parser")
            content = soup.find("div", {"class":"mw-content-text"})
            if content is not None:
                trackListBox = content.find("ol")
                songItems = trackListBox.findAll("li")
                for songItem in songItems:
                    songLink = songItem.find("a")
                    title = songLink.string
                    url = BASE_URL.format(songLink["href"])
                    song = Song(title)
                    song.setLink(url)
                    song.setArtist(self.getArtist())
                    self.songList.append(song)
        return self.songList
    
    def getLink(self):
        return self.link
    
    def __str__(self):
        return self.name
    
    def __eq__(self, other):
        return self.name == other.name and self.artist == other.artist

    def __repr__(self):
        return str(self)


# In[288]:


class Song:
    
    def __init__(self, title, lyrics=None, link=None, artist=None):
        self.title = title
        self.lyrics = lyrics
        self.link = link
        if type(artist) is str:
            self.artist = Artist(artist)
        else:
            self.artist = artist
    
    def getArtist(self):
        return self.artist
    
    def setArtist(self, artist):
        self.artist = artist
        
    def getTitle(self):
        return self.title
    
    def setLyrics(self, lyrics):
        self.lyrics = lyrics
        
    def getLyrics(self):
        if self.lyrics is None:
            self.lyrics = getLyrics(song)
        return self.lyrics
    
    def setLink(self, link):
        self.link = link
    
    def getLink(self):
        return self.link
    
    def __str__(self):
        return self.title
    
    def __repr__(self):
        return str(self)
    
    def __eq__(self, other): 
        return self.title == other.title and self.artist == other.artist


# In[301]:


class Billboard:
    
    def __init__(self, totalWeeks=1, chart=billboard.ChartData('hot-100')):
        self.songList = []
        songIndex = 0
        weekNum = 0
        while (weekNum < totalWeeks):
            while (songIndex < len(chart.entries)):
                chartSong = chart[songIndex]
                artistName = chartSong.artist
                for cut_off in MAIN_ARTIST_CUT_OFFS:
                    if cut_off in artistName:
                        artistName = artistName[:artistName.find(cut_off)]
                song = Song(title=chartSong.title, artist=artistName)
                if song not in self.songList:
                    self.songList.append(song)
                songIndex += 1
            weekNum += 1
            songIndex = 0
            chart = billboard.ChartData('hot-100', chart.previousDate)
    
    def getSongList(self):
        return self.songList
    
    def getArtistList(self):
        return set([song.getArtist() for song in self.songList])
    
    def __len__(self):
        return len(songList)


# In[263]:


class Genre:
    def __init__(self, genre):
        if genre not in GENRE_LIST:
            raise Exception('genre, {0} is not in the accepted genre list. Please use getGenreList() to find acceptable genres. '.format(genre))
        chart = billboard.ChartData('{0}-songs'.format(genre))
        billboardChart = Billboard(104, chart)
        self.artistList = billboardChart.getArtistList()
        self.songList = billboardChart.getSongList()
    
    def getArtistList(self):
        return self.artist
    
    def getSongList(self):
        return self.songList
    
    def getGenreList(self):
        return GENRE_LIST


# In[264]:


def getLyrics(song):
    artist = song.getArtist()
    title = song.getTitle()
    try:
        artistName = artist.getName()
        url = SEARCH_URL.format(artistName.replace(" ", "+"), title.replace(" ", "+"))
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
        lyrics = lyricBox.text.strip()
        song.setLyrics(lyrics)
        return lyrics
    except:
        return None


# In[265]:


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
            print(getLyrics( Song(args.title, Artist(args.artist) )))
        else:
            print(Artist(args.artist).getLyrics())
    elif args.genre:
        print([ song.getLyrics for song in Genre(args.genre).getSongList()])
    elif args.genrelist:
        print(GENRE_LIST)
    elif args.billboardchart:
        print([song.getLyrics for song in Billboard(args.billboardChart).getSongList()])
    else:
        raise Exception("An argument, such as -a artist -t title, is needed")


# In[266]:


if __name__ == '__main__':
    main()

