import os.path
from pathlib import Path
from typing import List

import arrow
import click
import yaml

from swps_tweet_download_client.application.file_merger import FileMerger
from swps_tweet_download_client.application.minio_downloader import MinioDownloader
from swps_tweet_download_client.config import dynaconf_settings, PUBLIC_CONFIG_FILE
from swps_tweet_download_client.domain.minio_credentials import MinioCredentials


@click.group()
def cli():
    pass


@cli.command("from_minio")
@click.option('--download_path', '-d', help='Directory to save tweets', type=click.Path())
@click.option('--phrase', '-p', help='Phrases to download (can be multiple)', multiple=True)
@click.option('--since', '-s', help='Download since in YYYY-MM-DD format')
@click.option('--until', '-u', help='Download until in YYYY-MM-DD format')
def download_tweets_from_minio(download_path: str, phrase: List[str], since: str, until: str):
    path = Path(download_path).absolute()
    phrases = list(phrase)
    since_arrow = arrow.get(since, 'YYYY-MM-DD')
    until_arrow = arrow.get(until, 'YYYY-MM-DD')
    print()
    print(f'Download path: {path}')
    print(f'Phrases: {phrases}')
    print(f'Since: {since_arrow.isoformat()[:10]}')
    print(f'Until: {until_arrow.isoformat()[:10]}')
    print()
    MinioDownloader(MinioCredentials.from_config(dynaconf_settings)).download_phrases_in_range(
        since=since_arrow,
        until=until_arrow,
        phrases=phrases,
        root_directory=download_path
    )


@cli.command("merge_files")
@click.option('--input_directory', '-i', help='Directory with saved tweets',
              type=click.Path(exists=True))
@click.option('--output_file', '-o',
              help='Destination file to save merged results, acceptable formats: csv, xlsx',
              type=click.Path())
def merge_files(input_directory: str, output_file: str):
    if os.path.splitext(output_file)[1] not in ['.csv', '.xlsx']:
        print('Not supported output extension, try .xlsx or .csv')
    else:
        print()
        print(f'Input file: {Path(input_directory).absolute()}')
        print(f'Output file: {Path(output_file).absolute()}')
        print()
        FileMerger().merge(input_directory, output_file)


@cli.command("generate_config")
@click.option('--endpoint', '-e', help='Minio endpoint', prompt=True)
@click.option('--access_key', '-a', help='Access key to connect', prompt=True)
@click.option('--secret_key', '-s', help='Secret key to connect', prompt=True)
def generate_config(endpoint: str, access_key: str, secret_key: str):
    config = {'minio': {
        'endpoint': endpoint,
        'access_key': access_key,
        'secret_key': secret_key
    }}
    with open(PUBLIC_CONFIG_FILE, 'w') as file:
        yaml.dump(config, file)
    print(f'config :: {config}')


def main():
    cli()
