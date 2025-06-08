import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import time
import json

st = time.time()
SPOTIFY_CLIENT_ID = '39efe78c60ec4915a4e6e0274e0fc240'
SPOTIFY_CLIENT_SECRET = '6e9b34f37b3e4ee0b94ba48260de98a3'
auth_manager = SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET)
sp = spotipy.Spotify(auth_manager=auth_manager)

df = pd.read_csv('storageListening/listening_history_2025.csv')  # Assume columns: 'song_name', 'artist_name'
df['genre'] = None
df['length_ms'] = None

# artist_metadata = {}
with open("metadata/artist_metadata.json", 'r') as f:
    artist_metadata = json.load(f)

# song_metadata = {}
with open("metadata/song_metadata.json", 'r') as f:
    song_metadata = json.load(f)

for i, row in df.iterrows():
    query = f"{row['track']} {row['artist']}"
    if row['track'] in song_metadata:
        df.at[i, 'length_ms'] = song_metadata[row['track']]
        if row['artist'] in artist_metadata:
            df.at[i, 'genre'] = artist_metadata[row['artist']]
        else:
            results = sp.search(q=query, type='track', limit=1)
            if results['tracks']['items']:
                track = results['tracks']['items'][0]
                artist_id = track['artists'][0]['id']
                artist = sp.artist(artist_id)
                genres = artist.get('genres', [])
                df.at[i, 'genre'] = ', '.join(genres)

    else:
        results = sp.search(q=query, type='track', limit=1)
        if results['tracks']['items']:
            track = results['tracks']['items'][0]
            df.at[i, 'length_ms'] = track['duration_ms']/1000

            song_metadata[row['track']] = track['duration_ms']/1000
            # Genre information is at the artist level
            # One thing I could do going forward, is saving artist genre info in a .json for future lookup instead
            # of repeat saving
            if row['artist'] in artist_metadata:
                df.at[i, 'genre'] = artist_metadata[row['artist']]
            else:
                artist_id = track['artists'][0]['id']
                artist = sp.artist(artist_id)
                genres = artist.get('genres', [])
                df.at[i, 'genre'] = ', '.join(genres)
                artist_metadata[row['artist']] = df.at[i, 'genre']

with open("metadata/artist_metadata.json", "w") as f:
    json.dump(artist_metadata, f)

with open("metadata/song_metadata.json", "w") as f:
    json.dump(song_metadata, f)


print(df)
df.to_csv('listening_history_with_metadata_2025.csv', index=False)

print('Runtime:', time.time()-st)
