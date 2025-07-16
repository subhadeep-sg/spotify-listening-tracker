import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import time
import json
from dotenv import load_dotenv
import os
import logging
from utils.discord_notifier import send_discord_alert

load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
root_dir = os.getenv('project_root_dir')
logger = logging.getLogger(__name__)


def spotify_authenticate():
    try:
        logger.info(f'Authenticating with Spotify Web API..')
        SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
        SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
        auth_manager = SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID,
                                                client_secret=SPOTIFY_CLIENT_SECRET)
        sp = spotipy.Spotify(auth_manager=auth_manager)
        return sp

    except Exception as e:
        logger.error(f'Spotify Authentication Error: {e}', exc_info=True)
        send_discord_alert(f'Spotify Authentication Error: {e}')
        raise


def query_search_spotipy(sp, query, artist):
    """
    Searches the Spotify Web API for a track and its main artist's genre information.

    :param sp: spotipy.Spotify
    Spotify client object
    :param query: str
    A search string combining track and artist name.
    :param artist: str
    Full artist name string directly from the dataset
    :return: tuple[float, str]
    A tuple containing track duration in seconds and genre string (both can be None if either unavailable).
    """
    logger.debug('Doing a query search..')
    genre_data, track_length = None, None

    if ', ' in artist:
        main_artist = artist.split(', ')[0]
    else:
        main_artist = artist

    artist_info = sp.search(q=main_artist, type='artist', limit=1)
    if artist_info['artists']['items']:
        artist_item = artist_info['artists']['items'][0]
        genres = artist_item.get('genres', [])
        if genres:
            genre_data = ', '.join(genres)
    else:
        logger.warning(f'No artist found for query: {artist}')

    results = sp.search(q=query, type='track', limit=1)

    if results['tracks']['items']:
        track_item = results['tracks']['items'][0]
        track_length = track_item['duration_ms'] / 1000
    else:
        logger.warning(f'{query} not found in sp.search()!')

    return track_length, genre_data


def update_meta_dataframe(sp, dataframe, meta_dataframe, from_start=False):
    """
    Updates a listening history DataFrame with genre and track duration metadata
    from local metadata files and, if necessary, querying the Spotify Web API.

    :param sp: spotipy.Spotify
    Spotify client object
    :param dataframe: pd.DataFrame
    Full listening history DataFrame
    :param meta_dataframe: pd.DataFrame
    Previously existing metadata DataFrame that will be updated with new records.
    :param from_start: str
    A flag to allow updating the entire metadata DataFrame instead of just adding new records.
    :return: pd.DataFrame
    Updated metadata DataFrame with genre and duration fields populated (if available).
    """
    os.makedirs(f'{root_dir}/metadata', exist_ok=True)

    missing_query_path = f'{root_dir}/metadata/missing_queries.json'

    if os.path.exists(missing_query_path):
        with open(missing_query_path, 'r') as f:
            missing_queries = json.load(f)
    else:
        missing_queries = {}

    with open(f"{root_dir}/metadata/artist_metadata.json", 'r') as f:
        artist_metadata = json.load(f)

    # song_metadata = {}
    with open(f"{root_dir}/metadata/song_metadata.json", 'r') as f:
        song_metadata = json.load(f)

    last_row_meta_df = meta_dataframe.tail(1)
    last_time_stamp = last_row_meta_df['iso_time'].iloc[0]

    last_index = dataframe[dataframe['iso_time'] == last_time_stamp].index[0]

    last_index += 1
    new_rows_processed = 0

    if from_start:
        last_index = 0

    while last_index < len(dataframe):
        logging.debug(f'Before update:\n{dataframe.iloc[last_index]}')

        track_name = dataframe.at[last_index, 'track']
        artist_name = dataframe.at[last_index, 'artist']
        query = f"{dataframe.at[last_index, 'track']} {dataframe.at[last_index, 'artist']}"

        if track_name in song_metadata:
            logger.debug(f'{track_name} already in song metadata')
            dataframe.at[last_index, 'length_ms'] = song_metadata[track_name]
            if artist_name not in artist_metadata:
                track_length, genre_data = query_search_spotipy(sp=sp, query=query, artist=artist_name)
                artist_metadata[artist_name] = genre_data

            elif artist_metadata[artist_name]:
                dataframe.at[last_index, 'genre'] = artist_metadata[artist_name]
            else:
                logger.debug(f'{artist_name} has no genre')

        elif artist_name in artist_metadata:
            logger.debug(f'{artist_name} already in artist metadata')
            dataframe.at[last_index, 'genre'] = artist_metadata[artist_name]
            query = f"{dataframe.at[last_index, 'track']} {dataframe.at[last_index, 'artist']}"
            track_length, artist_genre = query_search_spotipy(sp=sp, query=query, artist=artist_name)
            dataframe.at[last_index, 'length_ms'] = track_length
        else:
            logger.debug('Track and artist not in metadata, new entry..')
            query = f"{dataframe.at[last_index, 'track']} {dataframe.at[last_index, 'artist']}"
            track_length, artist_genre = query_search_spotipy(sp=sp, query=query, artist=artist_name)
            dataframe.at[last_index, 'genre'] = artist_genre
            dataframe.at[last_index, 'length_ms'] = track_length

            song_metadata[track_name] = track_length
            artist_metadata[artist_name] = artist_genre
        logging.debug(f'Updated row:\n{dataframe.iloc[last_index]}')
        if not dataframe.at[last_index, 'length_ms'] or not dataframe.at[last_index, 'genre']:
            if query not in missing_queries:
                logger.debug(f'{query} has data missing and has not been added to missing queries')
                missing_queries[query] = {
                    'track': track_name,
                    'artist': artist_name,
                    'iso_time': dataframe.at[last_index, 'iso_time']
                }
        elif query in missing_queries:
            del missing_queries[query]
            logger.debug(f'Removing {query} from missing queries since data is now available..')

        new_rows_processed += 1
        last_index += 1

    with open(missing_query_path, 'w') as f:
        json.dump(missing_queries, f, indent=2)

    with open(f"{root_dir}/metadata/artist_metadata.json", "w") as f:
        json.dump(artist_metadata, f, indent=2)

    with open(f"{root_dir}/metadata/song_metadata.json", "w") as f:
        json.dump(song_metadata, f, indent=2)

    logger.info(f'New rows processed: {new_rows_processed}')
    logger.info(f'Returning dataframe with genre and length_ms updated')
    logger.info(f'Previous meta dataframe: {len(meta_dataframe)} rows, New meta dataframe: {len(dataframe)} rows')
    return dataframe


def main():
    try:
        st = time.time()
        sp = spotify_authenticate()

        df = pd.read_csv(f'{root_dir}/data/spotify_data_2025.csv')
        df['genre'] = None
        df['length_ms'] = None

        df_with_metadata = pd.read_csv(f'{root_dir}/data/spotify_data_with_metadata_2025.csv')
        updated_df = update_meta_dataframe(sp=sp, dataframe=df, meta_dataframe=df_with_metadata, from_start=False)

        if updated_df:
            updated_df.to_csv(f'{root_dir}/data/spotify_data_with_metadata_2025.csv', index=False)

        logger.info(f'Runtime: {time.time() - st}')
    except Exception as e:
        logger.error(f'Unexplained error: {e}', exc_info=True)
        send_discord_alert(f'Unexplained error at metadata extract main(): {e}')


if __name__ == '__main__':
    main()
