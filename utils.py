from constant import *
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

def wait_for_element_by_css_selector(css_selector, wd):
    try:
        return WebDriverWait(wd, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, css_selector)))
    except TimeoutException:
        return None

def get_genres(wd):
  wd.get("https://www.beatport.com")
  return {
      genre.get_attribute('data-name') : genre.get_attribute('href')
      for genre in wd.find_elements_by_class_name('genre-drop-list__genre')
  }

def get_genre_charts(genre_link, wd):
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

    #TODO
    for i in range(1, chart_lenght + 1, 1):

        link = (
            wait_for_element_by_css_selector(
                f'li.bucket-item:nth-child({i}) > div:nth-child(3) > p:nth-child(1) > a:nth-child(1)',
                wd
            )
            .get_attribute('href')
        )

        wd.get(link)

        ul = wd.find_element_by_class_name('interior-track-content-list')
        lis = ul.find_elements_by_tag_name('li')

        for li in lis:
            k, v = li.find_elements_by_tag_name('span')
            if k in tracks.keys():
                tracks[k].append(v)

        print(tracks)
        wd.get(chart_link)

    return tracks

def select_genre(wd):
    genres = get_genres(wd)
    print('Enter the number of the desired genre and press enter.\n')
    for i, g in enumerate(genres.keys()):
        print(f'{i} - {g}')

    n = int(input())
    genre = list(genres.keys())[n]

    return genres[genre]

def select_chart(genre_link, wd):
    charts = get_genre_charts(genre_link, wd)
    print('Enter the number of the desired chart and press enter.\n')
    for i, c in enumerate(charts.keys()):
        print(f'{i} - {c}')

    n = int(input())
    chart = list(charts.keys())[n]

    return charts[chart]

def save_tracks(chart_link, tracks_dict):
    name = chart_link.split('/')[-2]
    df = pd.DataFrame(tracks_dict)
    df.to_csv(f'{name}.csv', index=False)
    print(f'CSV file save as {name}.csv')

def chart_tracks_to_csv(path):
    wd = webdriver.Firefox(executable_path=path)
    genre_link = select_genre(wd)
    chart_link = select_chart(genre_link, wd)
    tracks = get_tracks(chart_link, wd)
    save_tracks(chart_link, tracks)

def search_track(track, wd):
    wd.get('http://soundcloud.com')


def search_tracks(chart_csv, wd):
    tracks.fillna('', inplace=True)
    for _, track in tracks:
        string = (
            track.title + ' ' +
            track.artist + ' ' +
            track.remixers + ' ' +
            track.labels
        )
        wd.get(f'http://soundcloud.com/search?q={string}')
