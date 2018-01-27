# Lyrics Corpora
This Python API allows users to create a corpus of lyrical data from their favorite artist, genre, or billboard charts. This API differentiates itself from others similar to it by retrieving lyrics from songs and artists through searches (thereby allowing variation in name) and by allowing users to get collections of music from genres and billboard charts instead of just individual songs or artist discographies.  


## Install 

```python
pip install lyricscorpora
```
## Usage

### Getting lyrics from a song
```python
song = Song("The Weeknd", "Wicked Games")
getLyrics(song)
[out]: I left my girl back home...
```

### Getting artist info
```python
artist = Artist("Drake")
albumList = artist.getAlbumList()
print(albumList)
[out]: "Room for Improvement (2006)", "Comeback Season (2007)", ... "Scary Hours (2018)"
album = albumList[6]
print(album)
[out]: "Scary Hours (2018)"
songList = album.getSongList()
print(songList)
[out]: "God's Plan", "Diplomatic Immunity"
song = songList[1]
song.getLyrics()
[out]: "Yeah they wishin' and wishin' and wishin' and wishin'..."

```
### Getting artist corpus
```python
artist = Artist("Drake")
artist.getLyrics() #gets the lyrics to every song from every album by the artist
[out]: "You see the difference between me and you..."
```

### Getting lyrics from Billboard charts
```python
billboardChart = Billboard(52) #Gets song information from every song on the charts for the past 52 weeks
songList = billboardChart.getSongList()
print(songList)
[out]: "Havana, Perfect, Rockstar, .."
song = songList[0]
print(song.getLyrics)
[out]: "Havana, ooh na-na (ay)"
artist = song.getArtist()
print("Camila Cabello")
```

### Getting lyrics by genre
```python
GENRE_LIST = ["r-b-hip-hop", "country", "rock", "latin", "dance-electronic", "christian", "gospel"]
...
genre = Genre("r-b-hip-hop") #Gets the songs for the genre's top 50 songs for the past 2 years (must be from GENRE_LIST) 
genre.getArtistList()
[out]: "Bruno Mars & Cardi B", "Miguel", "Chris Brown"...
genre.getSongList()
[out]: "Finesse (remix)", "Skywalker", "Pills & Automobiles"...
```

## License
This project is licensed under the MIT License - see the LICENSE.md file for details
