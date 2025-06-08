Just wanted to make a document for self reference on things I didn't know and needed.

### Scopes:
1. User Profile Scopes

`user-read-private`: Access the user’s account information (e.g., display name, subscription level, etc.).

`user-read-email`: Access the user’s email address.
2. Playback Control Scopes

`user-modify-playback-state`: Control playback (e.g., play, pause, skip tracks).

`user-read-playback-state`: Access information about the user’s current playback (e.g., playing track, device state).

`user-read-currently-playing`: Access information about the currently playing track.
3. Listening History Scopes

`user-read-recently-played`: Access the user’s recently played tracks.

`user-top-read`: Access the user’s top tracks and artists (over short, medium, and long time ranges).
4. Playlist Scopes

`playlist-read-private`: Access the user’s private playlists.

`playlist-modify-private`: Create, modify, and delete the user’s private playlists.

`playlist-read-collaborative`: Access collaborative playlists the user has joined.

`playlist-modify-public`: Create, modify, and delete public playlists.
5. Library Scopes

`user-library-read`: Access the user’s saved tracks and albums.

`user-library-modify`: Save and remove tracks and albums from the user’s library.
6. Follow Scopes

`user-follow-read`: Access the user’s followed artists and users.

`user-follow-modify`: Follow or unfollow artists and other Spotify users.
7. Spotify Connect Scopes

`app-remote-control`: Control Spotify playback on connected devices.

`streaming`: Play music and control playback in the Spotify client (primarily used for SDKs like the Web Playback SDK).

