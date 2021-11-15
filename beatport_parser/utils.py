import re
import string
import logging
import pandas as pd
import numpy as np
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

logging.basicConfig(level='INFO')

def wait_for_element_by_css_selector(css_selector, wd):
    try:
        return WebDriverWait(wd, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, css_selector)))
    except TimeoutException:
        return None

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

def get_genres(wd):
    """
    Gets a dictionary with the genres and their links
    Parameters:
    ----------
    wd : selenium.webdriver

    Returns:
    ---------
    dict
    """
    wd.get("https://www.beatport.com")
    return {
        genre.get_attribute('data-name') : genre.get_attribute('href')
        for genre in wd.find_elements_by_class_name('genre-drop-list__genre')
    }

def get_genre_charts(genre_link, wd):
    """
    Gets a dictionary with the charts and their links
    Parameters:
    ----------
    genre_link : str

    wd : selenium.webdriver

    Returns:
    ---------
    dict
    """
    wd.get(genre_link)
    charts = {
        str(name.text + ' - ' + artist.text) : link.get_attribute('href')
        for name, artist, link in zip(
            wd.find_elements_by_class_name('chart-title'),
            wd.find_elements_by_class_name('chart-artists'),
            wd.find_elements_by_class_name('chart-url')
        )
    }

    tops = {
        top_chart.text: top_chart.get_attribute('href')
        for top_chart in wd.find_elements_by_class_name('view-top-hundred-tracks')
    }

    return {
        **charts,
        **tops
    }

def get_tracks(chart_link, wd):
    """
    Gets a dictionary containing all metadata for
    each track for the given chart

    Parameters:
    ----------
    chart_link : str

    wd : selenium.webdriver

    Returns:
    ---------
    dict
    """
    wd.get(chart_link)
    tracks = {
        'title': [title.text for title in wd.find_elements_by_class_name('buk-track-title')][1:],
        'artist': [artist.text for artist in wd.find_elements_by_class_name('buk-track-artists')][1:],
        'remixers': [rem.text for rem in wd.find_elements_by_class_name('buk-track-remixers')][1:],
        'LABEL': [],
        'RELEASED': [],
        'LENGTH': [],
        'BPM': [],
        'KEY': [],
    }

    chart_lenght = len(tracks['title'])

    for i in range(1, chart_lenght + 1):

        link = (
            wait_for_element_by_css_selector(
                f'li.bucket-item:nth-child({i}) > div:nth-child(3) > p:nth-child(1) > a:nth-child(1)',
                wd
            )
            .get_attribute('href')
        )

        wd.get(link)

        lis = (
            wd
            .find_element_by_class_name('interior-track-content-list')
            .find_elements_by_tag_name('li')
        )

        for li in lis:
            k, v = li.find_elements_by_tag_name('span')
            if k.text in tracks.keys():
                tracks[k.text].append(v.text)

        wd.get(chart_link)

    return tracks

def select_genre(wd):
    """
    Returns the selected genre link

    Parameters:
    ----------
    wd : selenium.webdriver

    Returns:
    ---------
    str
    """
    genres = get_genres(wd)
    print('Enter the number of the desired genre and press enter.\n')

    for i, g in enumerate(genres.keys()):
        print(f'{i} - {g}')

    n = int(input())
    return genres[list(genres.keys())[n]]

def select_chart(genre_link, wd):
    """
    Returns the selected chart link

    Parameters:
    ----------
    wd : selenium.webdriver

    Returns:
    ---------
    str
    """
    charts = get_genre_charts(genre_link, wd)
    print('Enter the number of the desired chart and press enter.\n')

    for i, c in enumerate(charts.keys()):
        print(f'{i} - {c}')

    n = int(input())
    return charts[list(charts.keys())[n]]

def save_tracks(chart_link, tracks_dict, save=True, format=True):
    """
    Creates and saves a dataframe with the chart metadata

    Parameters:
    ----------
    chart_link : str

    tracks_dict : dict
        Dictionary returned by get_tracks method

    save : bool
        If true it will save the dataframe into a csv file

    Returns:
    --------
    pd.DataFrame
    """
    name = chart_link.split('/')[-2]
    df = pd.DataFrame(tracks_dict)
    if format:
        df['duration'] = df['LENGTH']
        df['track_name'] = (
            df[['title', 'artist' ,'remixers']]
            .fillna('')
            .agg(lambda x: ' '.join(x), axis=1)
            .apply(clean_title)
        )
    if save:
        df.to_csv(f'{name}.csv', index=False)
        logging.info(f'CSV file save as {name}.csv')
    return df

def chart_tracks(path, save=True):
    """
    Allows user to search a chart from beatport
    and save the chart metadata

    Parameters:
    -----------
    path : str
        executable path for the webdriver

    save : bool
        If true it will save the dataframe into a csv file
    """
    wd = webdriver.Firefox(executable_path=path)
    genre_link = select_genre(wd)
    chart_link = select_chart(genre_link, wd)
    tracks = get_tracks(chart_link, wd)
    wd.close()
    return save_tracks(chart_link, tracks, save=save)
