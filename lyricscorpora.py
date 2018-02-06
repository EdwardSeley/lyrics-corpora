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

class NoLyricsException(Exception): 
    pass

class Artist:
    
    def __init__(self, artist_name):
        self.name = artist_name
        self.album_list = None
    
    def get_album_list(self):
        if self.album_list is None:
            page = requests.get(BASE_URL.format(self.name))
            soup = BeautifulSoup(page.content, "html.parser")
            headlines = soup.find_all("span", {"class", "mw-headline"})
            album_list = []
            for headline in headlines:
                link = headline.find("a")
                if link is not None:
                    title = link["title"]
                    album_title = title[title.find(":")+1:title.find(" (")]
                    album = Album(album_title, self, BASE_URL.format(link["href"]))
                    album_list.append(album)
            self.album_list = album_list
        return self.album_list
    
    def get_song_list(self):
        return [song for album in self.get_album_list() for song in album.get_song_list()]
    
    def get_lyrics(self):
        lyrics = ""
        for album in self.get_album_list():
            for song in album.get_song_list():
                try:
                    if song.lyrics is None:
                        page = requests.get(song.link)
                        soup = BeautifulSoup(page.content, 'html.parser')
                        lyric_box = soup.find('div', {'class': 'lyricbox'})
                        if lyric_box is None:
                            raise NoLyricsException("Could not find lyrics on song page")
                        for br in lyric_box.find_all('br'):
                            br.replace_with('\n')
                        song_lyrics = lyric_box.text.strip()
                        lyrics.join(song_lyrics)
                        song.set_lyrics(song_lyrics)
                    else:
                        lyrics.join(song.get_lyrics())
                except:
                    continue
        return lyrics
    
    def __str__(self):
        return "Artist(name={0})".format(self.name)
    
    def __repr__(self):
        return str(self)
    
    def __eq__(self, other): 
        return self.name == other.name
    
    def __hash__(self):
        return hash(self.name)
    
    
class Album:
    
    def __init__(self, album_name, artist_name, album_link=None):
        self.name = album_name
        self.artist = artist_name
        self.link = album_link
        self.song_list = []
    
    def get_song_list(self):
        if not self.song_list:
            link = self.link
            page = requests.get(link)
            soup = BeautifulSoup(page.content, "html.parser")
            content = soup.find("div", {"class": "mw-content-text"})
            if content is not None:
                track_list_box = content.find("ol")
                song_items = track_list_box.findAll("li")
                for song_item in song_items:
                    song_link = song_item.find("a")
                    title = song_link.string
                    url = BASE_URL.format(song_link["href"])
                    song = Song(title)
                    song.link = url
                    song.artist = self.artist
                    self.song_list = self.song_list.append(song)
        return self.song_list
    
    def __str__(self):
        return "Album(title={0}, artist={1})".format(self.name, self.artist)
    
    def __eq__(self, other):
        return self.name == other.name and self.artist == other.artist

    def __repr__(self):
        return str(self)

    
class Song:
    
    def __init__(self, song_title, song_lyrics=None, song_link=None, song_artist=None):
        self.title = song_title
        self.lyrics = song_lyrics
        self.link = song_link
        if type(song_artist) is str:
            self.artist = Artist(song_artist)
        else:
            self.artist = song_artist
        
    def get_lyrics(self):
        if self.lyrics is None:
            self.lyrics = get_lyrics(self)
        return self.lyrics
    
    def __str__(self):
        return "Song(title={0}, artist={1})".format(self.title, self.artist)
    
    def __repr__(self):
        return str(self)
    
    def __eq__(self, other): 
        return self.title == other.title and self.artist == other.artist

    
class Billboard:
    
    def __init__(self, total_weeks=1, chart_name='hot-100'):
        self.song_list = []
        song_index = 0
        week_num = 0
        chart = billboard.ChartData(chart_name)
        while week_num < total_weeks:
            while song_index < len(chart.entries):
                chart_song = chart[song_index]
                artist_name = chart_song.artist
                for cut_off in MAIN_ARTIST_CUT_OFFS:
                    if cut_off in artist_name:
                        artist_name = artist_name[:artist_name.find(cut_off)]
                song = Song(song_title=chart_song.title, song_artist=artist_name)
                if song not in self.song_list:
                    self.song_list = self.song_list.append(song)
                song_index += 1
            week_num += 1
            song_index = 0
            chart = billboard.ChartData('hot-100', chart.previous_date)

    def get_artist_list(self):
        return set([song.artist() for song in self.song_list])
    
    def __len__(self):
        return len(self.song_list)

    
class Genre:
    
    def __init__(self, genre):
        if genre not in GENRE_LIST:
            raise Exception('genre, {0} is not in the genre list. Use get_genre_list() to find genres. '.format(genre))
        billboard_chart = Billboard(104, '{0}-songs'.format(genre))
        self.artist_list = billboard_chart.get_artist_list()
        self.song_list = billboard_chart.song_list

    @staticmethod
    def get_genre_list():
        return GENRE_LIST

    
def get_lyrics(song):
    artist = song.artist
    title = song.title
    artist_name = artist.name
    url = SEARCH_URL.format(artist_name.replace(" ", "+"), title.replace(" ", "+"))
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')
    try:
        result_box = soup.find("li", {'class', 'result'})
        if result_box is None:
            raise NoLyricsException("Could not find the lyrics page in the results list")
        result_link = result_box.find("a", {'class', 'result-link'}, href=True)
        result_url = result_link.get('href')
        page = requests.get(result_url)
        soup = BeautifulSoup(page.text, 'html.parser')
        lyric_box = soup.find('div', {'class': 'lyricbox'})
        for br in lyric_box.findAll('br'):
            br.replace_with('\n')
        lyrics = lyric_box.text.strip
    except NoLyricsException:
        lyrics = ""
    song.lyrics = lyrics
    return lyrics


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
        print([song.get_lyrics for song in Genre(args.genre).song_list])
    elif args.genrelist:
        print(GENRE_LIST)
    elif args.billboardchart:
        print([song.get_lyrics() for song in Billboard(args.billboardChart).song_list])
    else:
        raise Exception("An argument, such as -a artist -t title, is needed")

        
if __name__ == '__main__':
    main()

