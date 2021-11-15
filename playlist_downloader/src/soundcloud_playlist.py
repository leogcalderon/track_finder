from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import logging
import spotipy
import os
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import re
import string


logging.basicConfig(level='INFO')
DRIVER_PATH = '/usr/local/bin/geckodriver'

def get_features(track_name):
    """
    Gets features from the Spotify API

    Parameters:
    -----------
    track_name : str

    Returns:
    --------
    dict
    """
    auth_manager = SpotifyClientCredentials()
    sp = spotipy.Spotify(auth_manager=auth_manager)
    id = sp.search(track_name, limit=1)['tracks']['items']
    if len(id) == 0:
        logging.info(f'[get_features] Track not found - {track_name}')
        return {}
    features = sp.audio_features(id[0]['id'])[0]
    features['duration'] = convert_to_time(features['duration_ms'])
    del features['duration_ms']
    return features

def convert_to_time(ms):
    """Converts ms into MM:SS format"""
    seconds = ms/1000
    minutes = int(seconds // 60)
    return f'{minutes}:{int(seconds % 60)}'

def clean_title(track_name):
    """
    Cleans the track title.
    Removes labels between [] and punctuations.

    Parameters:
    -----------
    track_name : str

    Returns:
    --------
    str
    """
    return (
        re.sub('[\[].*?[\]]', '', track_name)
        .lower()
        .replace('premiere', '')
        .replace('original', '')
        .translate(str.maketrans('', '', string.punctuation))
    )

def parse_playlist(playlist_link, driver_path=DRIVER_PATH):
    """
    Creates a dataframe from the Soundcloud playlist.

    Parameters:
    -----------
    playlist_link : str

    Returns:
    ---------
    pd.DataFrame
    """
    wd = webdriver.Firefox(executable_path=driver_path)
    wd.get(playlist_link)
    tracks = (
        wd
        .find_element_by_xpath('//*[@id="content"]/div/div[3]/div[1]/div/div[2]/div[2]/div/div[3]/div/ul')
        .find_elements_by_class_name('trackItem__trackTitle')
    )

    df = pd.DataFrame()
    for track in tracks:
        track_name = clean_title(track.text)
        features = get_features(track_name)
        df = df.append(
            {
                'track_name': track_name,
                **features
            },
            ignore_index=True,
        )
    wd.close()
    return df
