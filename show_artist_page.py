# import webbrowser
# import threading
# from flask import Flask, render_template, jsonify
# import spotipy
# from spotipy.oauth2 import SpotifyOAuth
# import os
#
# sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
#     client_id="39efe78c60ec4915a4e6e0274e0fc240",
#     client_secret="32bc09ab8f9f4e1996d3fb8b144c8f83",
#     redirect_uri="http://localhost:8888/callback",
#     scope="user-top-read"
# ))
#
# # top_tracks = sp.current_user_top_tracks(limit=5, time_range='short_term')
# top_artists = sp.current_user_top_artists(limit=5, time_range='short_term')
#
# # for idx, track in enumerate(top_tracks['items']):
# #     print(f"{idx + 1}: {track['name']} by {track['artists'][0]['name']}")
#
# # print('------------Last month top artists------------')
# # for idx, track in enumerate(top_artists['items']):
# #     # print(track.keys())
# #     print(f"{idx + 1}: {track['name']}, {track['images'][0]['url']}")
#
# # Sample data (you can replace this with your Spotify API data)
# artists = [
#     {
#         "name": artist['name'],
#         "image": artist['images'][0]['url'] if artist['images'] else "https://via.placeholder.com/200"
#         # Fallback image if no image exists
#     }
#     for artist in top_artists['items']
# ]
#
# # print("Templates folder content:", os.listdir("templates"))
#
# app = Flask(__name__, template_folder='templates')
#
#
# @app.route('/')
# def index():
#     return render_template('index.html', artists=artists)
#
#
# def open_browser():
#     # Open the default web browser to the Flask app URL
#     webbrowser.open_new('http://127.0.0.1:5000/')
#
#
# if __name__ == '__main__':
#     # Open the browser only if the app is run for the first time
#     if threading.current_thread().name == 'MainThread':
#         threading.Timer(0, open_browser).start()
#     app.run(debug=True)
