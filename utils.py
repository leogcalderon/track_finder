from constant import *
import time
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

    for i in range(1, chart_lenght + 1, 1):

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

def save_tracks(chart_link, tracks_dict, save=True):
    name = chart_link.split('/')[-2]
    df = pd.DataFrame(tracks_dict)
    if save:
        df.to_csv(f'{name}.csv', index=False)
        print(f'CSV file save as {name}.csv')
    return df

def chart_tracks(path, save=True):
    wd = webdriver.Firefox(executable_path=path)
    genre_link = select_genre(wd)
    chart_link = select_chart(genre_link, wd)
    tracks = get_tracks(chart_link, wd)
    wd.close()
    return save_tracks(chart_link, tracks, save=save)

def search_tracks(tracks):

    profile = webdriver.FirefoxProfile()
    profile.set_preference("browser.download.folderList", 2)
    profile.set_preference("browser.download.manager.showWhenStarting", False)
    profile.set_preference("browser.download.dir", 'PATH TO DESKTOP')
    profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/x-gzip")
    wd = webdriver.Firefox(firefox_profile=profile, executable_path=DRIVER_PATH)

    tracks.fillna('', inplace=True)

    for _, track in tracks.iterrows():
        search = (
            track.title + ' ' +
            track.artist + ' ' +
            track.remixers + ' ' +
            track.LABEL
        )

        wd.get(
            f'http://soundcloud.com/search?q={search}'
        )

        track_link = wait_for_element_by_css_selector('.soundTitle__title', wd)

        if track_link:
            track_link = track_link.get_attribute('href')
            wd.get('https://sctomp3.net')
            box = wd.find_element_by_class_name('form-control')
            box.send_keys(track_link)
            box.send_keys(Keys.RETURN)

            # IT GOES TOO FAST
            # AND DOESN'T DOWNLOAD
            download_button = wait_for_element_by_css_selector('.btn', wd)
            time.sleep(5)

            if download_button:
                download_button.send_keys(Keys.RETURN)
