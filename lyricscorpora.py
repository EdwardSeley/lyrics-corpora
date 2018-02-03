"""
Get lyrics from your favorite songs, artists, genres, and billboard charts! 
This is a WikiaLyrics API, but distinguishes itself from others like it (eg. lyric-api) 
because it searches for the artist and song through the lyrics.wikia.com website, 
thereby allowing for variations in the song or artist's name.
"""

import billboard
import requests
from bs4 import BeautifulSoup
import argparse

GENRE_LIST = ["r-b-hip-hop", "country", "rock", "latin", "dance-electronic", "christian", "gospel"]
SEARCH_URL = "http://lyrics.wikia.com/wiki/Special:Search?search={0}:{1}"
BASE_URL = "http://lyrics.wikia.com/{0}"
MAIN_ARTIST_CUT_OFFS = [" Featuring", " x ", " X ", " Duet With ", " &", ","]  # separates main artists from features


class Artist:
    
    def __init__(self, artistName):
        self.name = artistName
        self.albumList = None
    
    def get_name(self):
        return self.name
    
    def get_album_list(self):
        if self.albumList is None:
            page = requests.get(BASE_URL.format(self.get_name()))
            soup = BeautifulSoup(page.content, "html.parser")
            headlines = soup.findAll("span", {"class", "mw-headline"})
            albumList = []
            for headline in headlines:
                link = headline.find("a")
                if link is not None:
                    title = link["title"]
                    albumTitle = title[title.find(":")+1:title.find(" (")]
                    album = Album(albumTitle, self, BASE_URL.format(link["href"]))
                    albumList.append(album)
            self.albumList = albumList
        return self.albumList
    
    def get_song_list(self):
        return [song for album in self.get_album_list() for song in album.get_song_list()]
    
    def get_lyrics(self):
        lyrics = ""
        for album in self.get_album_list():
            for song in album.get_song_list():
                try:
                    if song.lyrics is None:
                        page = requests.get(song.getLink())
                        soup = BeautifulSoup(page.content, 'html.parser')
                        lyricBox = soup.find('div', {'class': 'lyricbox'})
                        for br in lyricBox.findAll('br'):
                            br.replace_with('\n')
                        songLyrics = lyricBox.text.strip()
                        lyrics += songLyrics
                        song.set_lyrics(songLyrics)
                    else:
                        lyrics += song.get_lyrics()
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
    
    
class Album:
    
    def __init__(self, albumName, artistName, albumLink=None):
        self.name = albumName
        self.artist = artistName
        self.link = albumLink
        self.songList = []
            
    def get_artist(self):
        return self.artist
    
    def get_song_list(self):
        if not self.songList:
            link = self.get_link()
            page = requests.get(link)
            soup = BeautifulSoup(page.content, "html.parser")
            content = soup.find("div", {"class": "mw-content-text"})
            if content is not None:
                trackListBox = content.find("ol")
                songItems = trackListBox.findAll("li")
                for songItem in songItems:
                    songLink = songItem.find("a")
                    title = songLink.string
                    url = BASE_URL.format(songLink["href"])
                    song = Song(title)
                    song.set_link(url)
                    song.set_artist(self.get_artist())
                    self.songList.append(song)
        return self.songList
    
    def get_link(self):
        return self.link
    
    def __str__(self):
        return self.name
    
    def __eq__(self, other):
        return self.name == other.name and self.artist == other.artist

    def __repr__(self):
        return str(self)

    
class Song:
    
    def __init__(self, songTitle, songLyrics=None, songLink=None, songArtist=None):
        self.title = songTitle
        self.lyrics = songLyrics
        self.link = songLink
        if type(songArtist) is str:
            self.artist = Artist(songArtist)
        else:
            self.artist = songArtist
    
    def get_artist(self):
        return self.artist
    
    def set_artist(self, songArtist):
        self.artist = songArtist
        
    def get_title(self):
        return self.title
    
    def set_lyrics(self, songLyrics):
        self.lyrics = songLyrics
        
    def get_lyrics(self):
        if self.lyrics is None:
            self.lyrics = get_lyrics(self)
        return self.lyrics
    
    def set_link(self, songLink):
        self.link = songLink
    
    def get_link(self):
        return self.link
    
    def __str__(self):
        return self.title
    
    def __repr__(self):
        return str(self)
    
    def __eq__(self, other): 
        return self.title == other.title and self.artist == other.artist

    
class Billboard:
    
    def __init__(self, totalWeeks=1, chartName='hot-100'):
        self.songList = []
        songIndex = 0
        weekNum = 0
        chart = billboard.ChartData(chartName)
        while (weekNum < totalWeeks):
            while (songIndex < len(chart.entries)):
                chartSong = chart[songIndex]
                artistName = chartSong.artist
                for cut_off in MAIN_ARTIST_CUT_OFFS:
                    if cut_off in artistName:
                        artistName = artistName[:artistName.find(cut_off)]
                song = Song(songTitle=chartSong.title, songArtist=artistName)
                if song not in self.songList:
                    self.songList.append(song)
                songIndex += 1
            weekNum += 1
            songIndex = 0
            chart = billboard.ChartData('hot-100', chart.previousDate)
    
    def get_song_list(self):
        return self.songList
    
    def get_artist_list(self):
        return set([song.get_artist() for song in self.songList])
    
    def __len__(self):
        return len(self.songList)

    
class Genre:
    
    def __init__(self, genre):
        if genre not in GENRE_LIST:
            raise Exception('genre, {0} is not in the genre list. Use get_genre_list() to find genres. '.format(genre))
        chart = billboard.ChartData('{0}-songs'.format(genre))
        billboardChart = Billboard(104, chart)
        self.artistList = billboardChart.get_artist_list()
        self.songList = billboardChart.get_song_list()
    
    def get_artist_list(self):
        return self.artist
    
    def get_song_list(self):
        return self.songList

    @staticmethod
    def get_genre_list(self):
        return GENRE_LIST

    
def get_lyrics(song):
    artist = song.get_artist()
    title = song.get_title()
    try:
        artistName = artist.get_name()
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
        song.set_lyrics(lyrics)
        return lyrics
    except:
        return None


def main():
    parser = argparse.ArgumentParser(description="Get lyrics from your favorite artists, genres, and billboard charts!")
    parser.add_argument("-a", "--artist",
                        help="Specify the artist's name",
                        required=False
                        )
    parser.add_argument("-t", "--title",
                        help="Specify the song's title",
                        required=False
                        )
    parser.add_argument("-g", "--genre",
                        help="Specify the genre of lyrics you would like to receive",
                        required=False
                        )
    parser.add_argument("-gl", "--genrelist",
                        help="Returns a list of the genres from which you can retrieve a corpus of lyrics",
                        required=False,
                        action='store_true'
                        )
    parser.add_argument("-b", "--billboardchart",
                        help="Specify the number of weeks for the billboard charts",
                        required=False
                        )
    
    args = parser.parse_args()
    
    if args.artist:
        if args.title:
            print(get_lyrics(Song(args.title, Artist(args.artist))))
        else:
            print(Artist(args.artist).get_lyrics())
    elif args.genre:
        print([song.get_lyrics for song in Genre(args.genre).get_song_list()])
    elif args.genrelist:
        print(GENRE_LIST)
    elif args.billboardchart:
        print([song.get_lyrics for song in Billboard(args.billboardChart).get_song_list()])
    else:
        raise Exception("An argument, such as -a artist -t title, is needed")

        
if __name__ == '__main__':
    main()

