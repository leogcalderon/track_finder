from src.downloader import download_tracks
from src.soundcloud_playlist import parse_playlist
import click
import logging
import pandas as pd

logging.basicConfig(level='INFO')

@click.command()

@click.option(
    '--playlist-link',
    default=None,
    help='Soundcloud playlist link to parse.'
)
@click.option(
    '--csv-path',
    default=None,
    help='path/to/csv/playlist.'
)
def main(playlist_link, csv_path):
    if playlist_link:
        playlist = parse_playlist(playlist_link).dropna()
    else:
        playlist = pd.read_csv(csv_path)
    download_tracks(playlist)

if __name__ == '__main__':
    main()
