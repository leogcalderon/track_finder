from decouple import config

DRIVER_PATH = config.('DRIVER_PATH', default='/usr/local/bin/geckodriver')