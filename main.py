import utils
from constant import *

if __name__ == '__main__':
    #utils.chart_tracks_to_csv(DRIVER_PATH)

    import pandas as pd
    import IPython
    from selenium import webdriver

    DRIVER_PATH = '/usr/local/bin/geckodriver'
    #wd = webdriver.Firefox(executable_path=DRIVER_PATH)
    utils.chart_tracks_to_csv(DRIVER_PATH)
    IPython.embed()

    tracks.fillna('', inplace=True)

    for idx, track in tracks.iterrows():
        search = (
            track.title + ' ' +
            track.artist + ' ' +
            track.remixers + ' ' +
            track.labels
        )
        IPython.embed()
