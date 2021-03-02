import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

def get_genres(webdriver):
  webdriver.get("https://www.beatport.com")
  return {
      genre.get_attribute('data-name') : genre.get_attribute('href')
      for genre in webdriver.find_elements_by_class_name('genre-drop-list__genre')
  }

def get_genre_charts(genre_link, webdriver):
  webdriver.get(genre_link)

  charts = {
      str(name.text + ' - ' + artist.text) : link.get_attribute('href')
      for name, artist, link in zip(
          webdriver.find_elements_by_class_name('chart-title'),
          webdriver.find_elements_by_class_name('chart-artists'),
          webdriver.find_elements_by_class_name('chart-url')
      )
  }

  tops = {
    top_chart.text: top_chart.get_attribute('href')
    for top_chart in webdriver.find_elements_by_class_name('view-top-hundred-tracks')
  }

  return {
    **charts,
    **tops
  }

def get_tracks(chart_link, webdriver):
    webdriver.get(chart_link)
    return {
        'title': [title.text for title in webdriver.find_elements_by_class_name('buk-track-title')][1:],
        'artist': [artist.text for artist in webdriver.find_elements_by_class_name('buk-track-artists')][1:],
        'remixers': [rem.text for rem in webdriver.find_elements_by_class_name('buk-track-remixers')][1:],
        'labels': [label.text for label in webdriver.find_elements_by_class_name('buk-track-labels')][1:],
        'released': [date.text for date in webdriver.find_elements_by_class_name('buk-track-released')][1:]
    }

def select_genre(webdriver):
    genres = get_genres(webdriver)
    print('Enter the number of the desired genre and press enter.\n')
    for i, g in enumerate(genres.keys()):
        print(f'{i} - {g}')

    n = int(input())
    genre = list(genres.keys())[n]

    return genres[genre]

def select_chart(genre_link, webdriver):
    charts = get_genre_charts(genre_link, webdriver)
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

def search_track(track, webdriver):
    webdriver.get('http://soundcloud.com')
    search_form = webdriver.find_element_by_class_name('headerSearch')
    box = search_form.find_element_by_tag_name('input')
    box.clean()
    box.send_keys(track)
    search_form.find_element_by_tag_name('button').send_keys(Keys.ENTER)
