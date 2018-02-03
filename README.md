# Lyrics Corpora
This Python API allows users to create a corpus of lyrical data from their favorite artist, genre, or billboard charts. This API differentiates itself from others similar to it by retrieving lyrics from songs and artists through searches (thereby allowing variation in name) and by allowing users to get collections of music from genres and billboard charts instead of just individual songs or artist discographies.  


## Install 

```python
pip install lyricscorpora
```

## Command Line Interface
```
(C:\Users\seley\Anaconda3) C:\Users\seley>lyricscorpora --help                                                          
usage: lyricscorpora [-h HELP] [-a ARTIST] [-t TITLE] [-g GENRE] [-gl GENRELIST] [-b BILLBOARDCHART]                                                                                                                                                                          
Get lyrics from your favorite songs, artists, genres, and billboard charts!

optional arguments:                                                                                                       
-h, --help                          Show this help message and exit                                                                   
-a ARTIST, --artist ARTIST          Specify the artist's name                                                                         
-t TITLE, --title TITLE             Specify the song's title                                                                          
-g GENRE, --genre GENRE             Specify the genre of lyrics you would like to receive                                             
-gl, --genrelist                    Returns a list of the available genres to pull from                                    
-b BILLBOARDCHART                   Specify the number of weeks for the billboard charts  
```
## Usage

### Getting module
```python
import lyricscorpora as lc
```

### Getting lyrics from a song
```python
song = lc.Song("The Weeknd", "Wicked Games")
lc.get_lyrics(song)
[out]: I left my girl back home...
```

### Getting artist info
```python
artist = lc.Artist("Drake")
albumList = artist.get_album_list()
print(albumList)
[out]: "Room for Improvement (2006)", "Comeback Season (2007)", ... "Scary Hours (2018)"
album = albumList[6]
print(album)
[out]: "Scary Hours (2018)"
songList = album.get_song_list()
print(songList)
[out]: "God's Plan", "Diplomatic Immunity"
song = songList[1]
song.get_lyrics()
[out]: "Yeah they wishin' and wishin' and wishin' and wishin'..."

```
### Getting artist corpus
```python
artist = lc.Artist("Drake")
artist.get_lyrics() #gets the lyrics to every song from every album by the artist
[out]: "You see the difference between me and you..."
```

### Getting lyrics from Billboard charts
```python
billboardChart = lc.Billboard(52) #Gets song information from every song on the charts for the past 52 weeks
songList = billboardChart.get_song_list()
print(songList)
[out]: "Havana, Perfect, Rockstar, .."
song = songList[0]
print(song.get_lyrics)
[out]: "Havana, ooh na-na (ay)"
artist = song.get_artist()
print("Camila Cabello")
```

### Getting lyrics by genre
```python
GENRE_LIST = ["r-b-hip-hop", "country", "rock", "latin", "dance-electronic", "christian", "gospel"]
...
genre = lc.Genre("r-b-hip-hop") #Gets the songs for the genre's top 50 songs for the past 2 years (must be from GENRE_LIST) 
genre.get_artist_list()
[out]: "Bruno Mars & Cardi B", "Miguel", "Chris Brown"...
genre.get_song_list()
[out]: "Finesse (remix)", "Skywalker", "Pills & Automobiles"...
```

## License
This project is licensed under the MIT License - see the LICENSE.md file for details
