from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from datetime import datetime
from urllib.request import urlretrieve
import difflib
import logging
import pandas as pd
from tqdm import tqdm
import src.config
import os

logging.basicConfig(level='INFO')
DRIVER_PATH = '/usr/local/bin/geckodriver'

def get_seconds(duration):
    """Converts a string duration into seconds"""
    if len(duration.split(':')) == 2:
        min, seconds = duration.split(':')
        return int(min)*60 + int(seconds)
    return float('inf')

def search_track(webdriver, search):
    """
    Searchs for a particular track in slider
    website and returns the results table.

    Parameters:
    ----------
    webdriver : selenium.webdriver
    search : str
        track name to search

    Returns:
    --------
    selenium.webdriver.firefox.webelement.FirefoxWebElement
    """
    webdriver.get('https://slider.kz')
    search_form = webdriver.find_element_by_xpath('//*[@id="buttonSearch"]/input')
    search_form.send_keys(search)
    search_form.send_keys(Keys.RETURN)
    results = webdriver.find_element_by_xpath('//*[@id="liveaudio"]')
    webdriver.implicitly_wait(5)
    return results

def analize_results(results, track_duration, search):
    """
    Creates a dictionary with name, timedelta, string similarity with the
    original track name and the link for each track in the results table.

    Parameters:
    -----------
    results : selenium.webdriver.firefox.webelement.FirefoxWebElement
    track_duration : str
        Duration in the form MM:SS
    search : str
        track name to search

    Returns:
    --------
    list
    """
    return [
        {
            'name': name.text,
            'timedelta': abs(
                get_seconds(track_duration) - get_seconds(duration.text)
            ),
            'matching': difflib.SequenceMatcher(None, name.text, search).ratio(),
            'link': link
        }
        for name, duration, link in zip(
            results.find_elements_by_class_name('ui360'),
            results.find_elements_by_class_name('trackTime'),
            [
                link.find_element_by_tag_name('a')
                for link in results.find_elements_by_class_name('trackDownload')
            ]
        )
    ]

def download_best_match(results_list, path='downloads'):
    """
    Compares all results and downloads the best match. To get the best match
    this function select the result with the closest duration and higher
    track name similarity.

    Parameters:
    -----------
    results_list : list
        Containing all dictionaries for all the results
    """
    if not os.path.exists(path):
        os.makedirs(path)

    best_match = (
        sorted(
            results_list,
            key=lambda x: (x['timedelta'], 1 - x['matching'])
        )[0]
    )
    if best_match['name'] != 'undefined':
        logging.info(f'[download_best_match] Downloading {best_match["name"]}')
        urlretrieve(best_match['link'].get_attribute('href'), f'{path}/{best_match["name"]}.mp3')

def download_track(search, duration, driver_path=DRIVER_PATH):
    """
    Downloads a track with slider.

    Parameters:
    ----------
    search : str
        track name to search
    duration : str
        track duration in the format MM:SS
    driver_path : str
        executable path for the webdriver
    """
    wd = webdriver.Firefox(executable_path=driver_path)
    results = search_track(wd, search)
    results_list = analize_results(results, duration, search)
    download_best_match(results_list)
    wd.close()

def download_tracks(df):
    """
    Searchs and download if exists all the tracks in the dataframe.

    Parameters:
    -----------
    df : pd.DataFrame
        Track names must be in 'track_name' column and duration in the format
        MM:SS in the 'duration' column.
    """
    for search, duration in tqdm(zip(df['track_name'], df['duration'])):
        download_track(search, duration)
