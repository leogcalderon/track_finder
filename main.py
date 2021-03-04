import utils
from constant import *

if __name__ == '__main__':
    tracks = utils.chart_tracks(DRIVER_PATH)
    utils.search_tracks(tracks)
