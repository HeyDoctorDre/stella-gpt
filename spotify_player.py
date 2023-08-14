
# * Utilities
import AppOpener
import os
import requests
from dotenv import load_dotenv
import psutil

import json
import webbrowser
import time

# * Spotify packages
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# * Custom open function
from commands import open_app, is_open


class Spotify_Player:
    
    def __init__(self):
        """
        
        """
        # * Whats needed?
        # * - username
        # * - client id, client secret, and redirect uri

        
        self.spotifyObject = spotipy.Spotify(
            # auth=token,
            auth_manager=SpotifyOAuth(
                client_id=os.getenv('SPOTIPY_CLIENT_ID'),
                client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
                redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
                scope=[
                    "streaming", 
                    "user-modify-playback-state", 
                    "user-read-playback-state",
                    "playlist-read-private"
                ],
            )
        )

        self.user = self.spotifyObject.current_user()
        self.device_id: str = ""
        self.is_installed = self.is_spotify_installed()    
    
    def resume_playback():
        """
        Resume the user's current playback on spotify
        """
    
    def pause_playback():
        """
        Pause the user's current playback on Spotify.
        """

    def play_track(self, track: str):
        """
        play a track/song requested by the user on Spotify.
        """


        # * 1. Open spotify, if not already open.
        # * 2. Get the device ID (Either for the computer or the web browser)
        # * 3. Search for the requested item.
        # * 4. Play the requested item. 
        
        self.wait_for_device()

        # * If there is an active device, we can can play something on spotify.
        if self.device_id:
            searchResults = self.spotifyObject.search(q=track, type="track", limit=1)

            # Play the song
            track = searchResults["tracks"]["items"][0]["uri"]

            self.spotifyObject.start_playback(
                device_id=self.device_id,
                uris=[track]
            )
        
        # * Otherwise, the user must be informed to log in.


    def play_playlist(self, playlist: str):
        """
        play a playlist requested by the user on Spotify
        """

        self.wait_for_device()

        # * If there is an active device, we can can play something on spotify.
        if self.device_id:
            # searchResults = self.spotifyObject.search(q=track, type="track", limit=1)

            searchResults = self.get_playlist(playlist)

            # Play the playlist
            playlist_uri = searchResults["playlists"]["items"][0]["uri"]

            self.spotifyObject.start_playback(
                device_id=self.device_id,
                context_uri=playlist_uri
            )
        

    
    def play_album(self, album: str):
        """
        play an album requested by the user on Spotify.
        """

        self.wait_for_device()

        # * If there is an active device, we can can play something on spotify.
        if self.device_id:
            searchResults = self.spotifyObject.search(q=album, type="album", limit=1)

            # Play the song
            album = searchResults["albums"]["items"][0]["uri"]

            self.spotifyObject.start_playback(
                device_id=self.device_id,
                context_uri=album
            )
    
    # *********************
    # * Utility methods
    # *********************

    def is_spotify_installed(self) -> bool:
        """
        Checks if spotify is installed on the user's computer.
        """
        installed_apps = AppOpener.give_appnames(upper=False)
        
        for app in installed_apps:
            if "spotify" in app:
                return True
        
        return False


    def open_spotify(self):
        """
        Opens Spotify if it isn't already opened. If Spotify is not installed,
        then it is opened on the web browser.
        """

        # * Check if spotify is installed and can be opened.
        # is_installed = self.is_spotify_installed()

        # * If spotify is installed and not open, open on the computer.
        if self.is_installed:
            open_app("spotify")

        # * Otherwise, If not installed, open it on the web browser

    def find_device_id(self, is_web_browser: bool = False) -> str:
        """
        Finds the id of the device to be used to interact with Spotify.
        """

        devices = self.spotifyObject.devices()["devices"]

        # * If there are no available devices
        if not devices:
            return ""        

        for device in devices:

            device_id = device["id"]

            device_name = str.lower(device["name"])

            device_type = str.lower(device["type"])

            if is_web_browser:
                if "browser" in device_name:
                    return device_id
            
            else:
                if "browser" not in device_name and \
                "computer" in device_type:
                    return device_id

    def wait_for_device(self):

        # * If spotify is not opened, open it and wait for device
        # * Otherwise, just set the device id

        if not is_open("spotify", include_exe=True):
            self.open_spotify()

            # * If no current device, find and set the current device
            # * Loop and wait for the device to show, the set the device id

            temp_device_id = ""
            for i in range(2):
                time.sleep(5)

                temp_device_id = self.find_device_id()

                if temp_device_id:
                    self.set_device_id(temp_device_id)  
                    break
        else:
            temp_device_id = self.find_device_id()
            self.set_device_id(temp_device_id)

    def get_playlist(self, playlist: str) -> json:
        """
        Return the playlist searched for by the user.
        """

        # * In order the playlist a user searches for, we have to make 
        # * our own request to the Spotify API.
        # * The reason is that the results return the playlists owned/followed
        # * by the user at the top. 
        # * However, the python Spotipy library does not.
        

        # * First we need the token to make the request
        file = open('.cache')
        data = json.load(file)
        token = data["access_token"]

        url = "https://api.spotify.com/v1/search"

        url_query = "?q={playlist}&type=playlist&limit=3".format(playlist=playlist)

        header = self.get_auth_header(token)

        response = requests.get(
            url=url + url_query,
            headers=header
        )

        return response.json()

    # *********************
    # * Get and Set methods 
    # *********************
    def set_device_id(self, device_id: str):
        self.device_id = device_id

    # * This header is needed to make requests to the Spotify API.
    # * We only need this for playing playists
    def get_auth_header(self, token: str):
        return {"Authorization": "Bearer "+ token}
