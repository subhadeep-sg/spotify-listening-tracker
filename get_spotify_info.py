import base64
import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import requests

scope = (
    "user-read-recently-played "
    # "user-top-read"
)

load_dotenv()
sp_oauth = SpotifyOAuth(
    client_id=os.getenv('SPOTIPY_CLIENT_ID'),
    client_secret=os.getenv('SPOTIPY_CLIENT_SECRET'),
    redirect_uri="http://localhost:5500",
    # redirect_uri='https://webhook.site/78f181cb-9a03-4083-bd97-498425695c50',
    scope=scope
)


# Prepare the token URL and the request headers
token_url = "https://accounts.spotify.com/api/token"

# Prepare the data to send in the POST request
data = {
    'grant_type': 'authorization_code',
    'code': 'BQClfoDnJFmDlGawY-v9DPnlzRZ7J0k5g0H6pF5hogv_ZHb74jzxdBAhLjpAcvDWxhR1akD7BosEMTzBwNo37_hz-jXRD58udUT-wE28wiVYw3294J0JcaZuLOUGgJZz6iPa0AB6LmuQuKxJImORWcqDe_9y0eQHJg7-4Dda-nMTnJoZ2-nagelIHSqLejQFO9S2pzp6QIW0kZ16QQ0Irci0bUMAfzbWdxs',  # This is the code you received
    'redirect_uri': "http://localhost:5500",
}

# Prepare the Authorization header with base64 encoded client ID and client secret
auth_header = {
    'Authorization': 'Basic ' + base64.b64encode(f"{'39efe78c60ec4915a4e6e0274e0fc240'}:{'37ace1fa5cdb415a91be8fa9a672d2b5'}".encode()).decode('utf-8')
}

# Send POST request to exchange authorization code for tokens
response = requests.post(token_url, data=data, headers=auth_header)

# Parse the response JSON to get access and refresh tokens
tokens = response.json()

if 'access_token' in tokens and 'refresh_token' in tokens:
    access_token = tokens['access_token']
    refresh_token = tokens['refresh_token']
    print(f"Access Token: {access_token}")
    print(f"Refresh Token: {refresh_token}")
else:
    print("Error getting tokens:", tokens)

# # Try to get cached token
# token_info = sp_oauth.get_cached_token()
#
# # If no token found, go through the authentication process
# if not token_info:
#     auth_url = sp_oauth.get_authorize_url()
#     print(f"Go to the following URL to authorize: {auth_url}")
#     response_url = input("Paste the redirected URL here: ")
#     token_info = sp_oauth.get_access_token(response_url)
#
# access_token = token_info['access_token']
# print(access_token)
# sp = spotipy.Spotify(auth=access_token)
#
# # Get the last 50 recently played tracks
# results = sp.current_user_recently_played(limit=50)

# # Print the results
# for idx, item in enumerate(results['items']):
#     track = item['track']
#     print(f"{idx + 1}. {track['name']} by {', '.join(artist['name'] for artist in track['artists'])}")

# sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
#     client_id="39efe78c60ec4915a4e6e0274e0fc240",
#     client_secret="32bc09ab8f9f4e1996d3fb8b144c8f83",
#     # redirect_uri="http://localhost:8888/callback",
#     scope="user-top-read"
# ))

# top_tracks = sp.current_user_top_tracks(limit=10, time_range='short_term')
# top_artists = sp.current_user_top_artists(limit=10, time_range='short_term')
#
# for idx, track in enumerate(top_tracks['items']):
#     print(f"{idx + 1}: {track['name']} by {track['artists'][0]['name']}")
#
# print('------------Last month top artists------------')
# for idx, track in enumerate(top_artists['items']):
#     print(f"{idx + 1}: {track['name']}")
#
# six_month_tracks = sp.current_user_top_tracks(limit=25, time_range='medium_term')
# six_month_artists = sp.current_user_top_artists(limit=25, time_range='medium_term')
#
# print('------------Six month top artists------------')
# for idx, track in enumerate(six_month_artists['items']):
#     print(f"{idx + 1}: {track['name']}")
#
# all_time_tracks = sp.current_user_top_tracks(limit=25, time_range='long_term')
# all_time_artists = sp.current_user_top_artists(limit=25, time_range='long_term')
#
# for idx, track in enumerate(all_time_tracks['items']):
#     print(f"{idx + 1}: {track['name']} by {track['artists'][0]['name']}")
#
# print('------------All Time Top Artists------------')
# for idx, track in enumerate(all_time_artists['items']):
#     print(f"{idx + 1}: {track['name']}")