from decouple import config

DRIVER_PATH = config('DRIVER_PATH', default='/usr/local/bin/geckodriver')
DELAY = config('DELAY', default=10)
DOWNLOAD_DIR = config('DOWNLOAD_DIR', default='/home/leonardo/Downloads')
