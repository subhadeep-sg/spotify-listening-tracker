import os.path
import time
import spotipy
from pytz import timezone
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
from datetime import datetime, timedelta
from dateutil import parser

"""
It seems like I can collect about 40 or so tracks at a time and then the API restricts access.
So to account for this, I'll need to do perform a periodic scan of the listening history
to pick up on the most recently played tracks.

A particular thing to note is to avoid overlap of entries. I want each entry to be unique (on the time not on track name).
"""
storage_path = './storageListening'
scope = (
    "user-read-recently-played "
    # "user-top-read"
)
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id="39efe78c60ec4915a4e6e0274e0fc240",
    client_secret="6e9b34f37b3e4ee0b94ba48260de98a3",
    redirect_uri="http://localhost:5000",
    scope=scope
))

one_day_ago = datetime.now() - timedelta(days=1)
one_day_ago_timestamp = int(one_day_ago.timestamp() * 1000)

recent_tracks = sp.current_user_recently_played(limit=50, after=one_day_ago_timestamp)
print(f"Asking Spotify for tracks after: {datetime.utcfromtimestamp(one_day_ago_timestamp / 1000)} UTC")
print(f"Number of tracks fetched: {len(recent_tracks['items'])}")

# recent_tracks = sp.current_user_recently_played(limit=50)
# for i, item in enumerate(recent_tracks['items']):
#     print(f"{i+1}. {item['track']['name']} played at {item['played_at']}")

current_year = datetime.now().year
if os.path.exists(f'{storage_path}/listening_history_{current_year}.csv'):
    df = pd.read_csv(f'{storage_path}/listening_history_{current_year}.csv')
else:
    df = pd.DataFrame(columns=['track', 'artist', 'date', 'est_time', 'ist_time', 'iso_time'])

for i, item in enumerate(recent_tracks['items']):
    track = item['track']
    date_played = item['played_at'].split('T')[0]
    utc_time = parser.isoparse(item['played_at'])
    ist_time = utc_time.astimezone(timezone('Asia/Kolkata'))
    est_time = utc_time.astimezone(timezone('America/New_York'))
    artists = ', '.join(artist['name'] for artist in track['artists'])
    # print(f"{i}, Track: {track['name']} by {track['artists'][0]['name']}")
    # print(f"Played at: {item['played_at']}")
    # print("-" * 40)
    listening_record = {'track': track['name'], 'artist': artists,#track['artists'][0]['name'],
                        'date': date_played,
                        'est_time': est_time, 'ist_time': ist_time,
                        'iso_time': item['played_at']
                        }

    # Check first if this listening record has already been added or not
    if (#listening_record['track'] not in df['track'].values and
            listening_record['iso_time'] not in df['iso_time'].values):
        df.loc[len(df)] = listening_record
    else:
        pass
        print(f"This record already exists: {listening_record['track']}, EST: {listening_record['est_time']}")

df = df.sort_values(by='iso_time', ascending=True)
df.to_csv(f'{storage_path}/listening_history_{current_year}.csv', index=False)

