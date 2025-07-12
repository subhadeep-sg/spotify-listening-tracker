import time
import os
from dotenv import load_dotenv
import spotipy
from pytz import timezone
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
from datetime import datetime, timedelta
from dateutil import parser
import logging

load_dotenv()
root_dir = os.getenv('project_root_dir')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
current_year = datetime.now().year


def read_recently_played():
    """
    Creates a Spotipy `Spotify` object using OAuth credentials loaded
    from environment variables. The object is authorized with the
    `user-read-recently-played` scope, allowing access to the current user's recent
    listening history.
    Environment Variables Required:
        - SPOTIFY_CLIENT_ID
        - SPOTIFY_CLIENT_SECRET
    :return:spotipy.Spotify object
    An authenticated Spotify Web API client instance.

    Raises:
        spotipy.oauth2.SpotifyOAuthError: If authentication fails due to missing/invalid credentials.
    """
    logger.info('Generating spotipy.Spotify class object based on private user keys..')
    scope = (
        "user-read-recently-played "
        # "user-top-read"
    )
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=os.getenv("SPOTIFY_CLIENT_ID"),
        client_secret=os.getenv('SPOTIFY_CLIENT_SECRET'),
        redirect_uri=os.getenv('redirect_uri'), #"http://127.0.0.1:5000",
        scope=scope
    ))
    logger.info('Returning spotipy.Spotify class object...')
    return sp


def extract_time_based_recent_played(spotipy_object, timeframe=1, time_type='day'):
    """
    Extracts recently played tracks from the Spotify Web API within a given timeframe.
    :param spotipy_object: spotipy.Spotify
    An authenticated Spotipy client object.
    :param timeframe: int, optional
    The number of time units (days/hours) to look back for played tracks. Default is 1.
    :param time_type: str, optional
           The type of time window to use ('day' supported currently). Default is 'day'.
    :return: dict
           A dictionary containing recently played track data returned by the Spotify API.
           If an error occurs, returns an empty dictionary.
    """
    try:
        logger.info(f'Extracting recent played from Spotify Web API..')
        one_day_ago = datetime.now() - timedelta(days=timeframe)
        timestamp = int(one_day_ago.timestamp() * 1000)

        recent_tracks = spotipy_object.current_user_recently_played(limit=50, after=timestamp)
        logger.info(f"Receiving tracks after: {datetime.utcfromtimestamp(timestamp / 1000)} UTC")
        logger.info(f"Number of tracks fetched: {len(recent_tracks['items'])}")
        return recent_tracks

    except Exception as e:
        logger.error(f'Failed to extract from Spotify Web API: {e}', exc_info=True)


def storage_pipeline(tracks):
    """
    Processes and stores Spotify track play history into a yearly CSV file.
    Reads the existing listening history for the current year (if present),
    appends any new tracks from the provided API `tracks` response, and returns the
    updated DataFrame.
    Duplicate tracks based on unique `iso_time` are ignored.
    The function handles:
    - Schema validation of existing data
    - Parsing of new Spotify play records
    - Timezone conversion to EST and IST
    - Appending and sorting the final dataset
    :param tracks: dict,
    A dictionary returned by the Spotify Web API `current_user_recently_played()` endpoint.
    :return: pd.DataFrame
    Updated listening history DataFrame including newly added tracks.
    If no new tracks, returns existing or empty DataFrame.

    Raises:
        ValueError: If the existing CSV file has unexpected column structure.
    """
    logger.info(f'Starting storage pipeline...')
    if os.path.exists(f'{root_dir}/data/spotify_data_{current_year}.csv'):
        dataframe = pd.read_csv(f'{root_dir}/data/spotify_data_{current_year}.csv')
        column_list = ['track', 'artist', 'date', 'est_time', 'ist_time', 'iso_time']

        if list(dataframe.columns) != column_list:
            raise ValueError(f"Existing dataframe doesn't match expected: {column_list}")
    else:
        dataframe = pd.DataFrame(columns=['track', 'artist', 'date', 'est_time', 'ist_time', 'iso_time'])

    new_track_count = 0
    new_rows = []

    items = tracks.get('items', [])
    if not items:
        logger.warning(f'No tracks found!')
        return dataframe

    for i, item in enumerate(items):
        # Check if iso_time record exists (this will be unique per record).
        if item['played_at'] not in dataframe['iso_time'].values:
            new_track_count += 1
            track = item['track']
            date_played = item['played_at'].split('T')[0]
            artists = ', '.join(artist['name'] for artist in track['artists'])
            utc_time = parser.isoparse(item['played_at'])
            ist_time = utc_time.astimezone(timezone('Asia/Kolkata'))
            est_time = utc_time.astimezone(timezone('America/New_York'))

            track_row = {
                'track': track['name'],
                'artist': artists,
                'date': date_played,
                'est_time': est_time,
                'ist_time': ist_time,
                'iso_time': item['played_at']
            }
            new_rows.append(track_row)
            logger.info(f'Added track: {track_row["track"]}, timestamp: {track_row["iso_time"]}')

    dataframe = pd.concat([dataframe, pd.DataFrame(new_rows)], ignore_index=True)
    dataframe = dataframe.sort_values(by=['iso_time'], ascending=True)
    logger.info(f'Added {new_track_count} new tracks.')
    logger.info(f'Returning dataframe with total {len(dataframe)} tracks..')
    return dataframe


if __name__ == '__main__':
    start = time.time()
    logger.info(f"Script run at: {datetime.now()}")

    sp = read_recently_played()
    recent_tracks = extract_time_based_recent_played(sp, timeframe=1, time_type='day')
    df = storage_pipeline(tracks=recent_tracks)

    os.makedirs(f'{root_dir}/data', exist_ok=True)
    df.to_csv(f'{root_dir}/data/spotify_data_{current_year}.csv', index=False)

    logger.info(f'Writing into ./data/spotify_data_{current_year}.csv')
    logger.info(f'Runtime: {time.time()-start}')
