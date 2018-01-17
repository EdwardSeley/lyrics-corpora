import billboard
import requests
from bs4 import BeautifulSoup

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

def getBillboardCorpus(totalWeeks=1):
    songIndex = 0
    weekNum = 0
    cut_off_list = [" Featuring", " x ", " X ", " Duet With ", " &", ","]
    music_collection = dict({})
    chart = billboard.ChartData('hot-100')
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
                    print(song)
            songIndex += 1
        weekNum += 1
        songIndex = 0
        chart = billboard.ChartData('hot-100', chart.previousDate)
    return music_collection

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

def getSongs(album):
    link = album[1]
    page = requests.get(link)
    soup = BeautifulSoup(page.content, "html.parser")
    content = soup.find("div", {"class":"mw-content-text"})
    if content is not None:
    trackListBox = content.find("ol")
    songItems = trackListBox.findAll("li")
    songs = []
    for songItem in songItems:
        songLink = songItem.find("a")
        title = songLink.string
        url = "http://lyrics.wikia.com{0}".format(songLink["href"])
        songs.append((title, url))
    return songs
    
billboardCorpus = getBillboardCorpus(totalWeeks=2)
drakeCorpus = getArtistCorpus("Drake")

drakeLyrics = ""
for album in drakeCorpus.keys():
    for song in drakeCorpus[album]:
        drakeLyrics += drakeCorpus[album][song]


