import utils
from constant import *

if __name__ == '__main__':
    #tracks = utils.chart_tracks(DRIVER_PATH)
    import pandas as pd
    tracks = pd.read_csv('best-new-deep-house-march.csv')
    utils.search_tracks(tracks)
