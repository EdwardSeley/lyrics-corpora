# Lyrics Corpora
This Python API allows users to create a corpus of lyrical data from their favorite artist, genre, or billboard charts. This API differentiates itself from others similar to it by retrieving lyrics from songs and artists through searches (thereby allowing variation in name) and by allowing users to get collections of music from genres and billboard charts instead of just individual songs or artist discographies.  


## Install 

```python
pip install lyricscorpora
```
## Usage

### Getting lyrics from a song
```python
getLyrics("The Weeknd", "Wicked Games")
[out]: I left my girl back home...
```

### Getting lyrics from an artist
```python
corpus = getArtistCorpus("Drake") #every Drake song from all of his albums and mixtapes
corpus.keys()
[out]: "Room for Improvement (2006)", "Comeback Season (2007)", ... "Scary Hours (2018)"
corpus[Scary Hours].keys()
[out]: "God's Plan", "Diplomatic Immunity"
corpus["Scary Hours]["Diplomatic Immunity"]
[out]: "Yeah they wishin' and wishin' and wishin' and wishin'..."
corpusToString(corpus) #puts all of the Drake lyrics into a string
[out]: You see the difference between me and you...
```

### Getting lyrics from Billboard charts
```python
corpus = getBillboardCorpus(52) #Gets the lyrics from every song on the hot 100 from the last 52 weeks
corpus.keys()
[out]: "Camila Cabello", "Ed Sheeran", "Post Malone", "Bruno Mars"...
corpus["Camila Calello"].keys()
[out]: "Havana", "Never Be the Same"
corpus["Camila Calello"]["Havana"]
[out]: "Havana, ooh na-na (ay)"
```

### Getting lyrics by genre
```python
GENRE_LIST = ["r-b-hip-hop", "country", "rock", "latin", "dance-electronic", "christian", "gospel"]
...
corpus = getGenreCorpus("r-b-hip-hop") #Gets the lyrics for the genre's top 50 songs for the past 2 years (must be from GENRE_LIST) 
corpus.keys()
[out]: "Bruno Mars & Cardi B", "Miguel", "Chris Brown"...
```
