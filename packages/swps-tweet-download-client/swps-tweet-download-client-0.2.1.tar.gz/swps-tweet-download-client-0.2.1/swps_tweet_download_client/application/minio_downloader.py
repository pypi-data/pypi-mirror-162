import os
import pathlib
import traceback
from typing import List

from arrow import Arrow
from minio import Minio

from swps_tweet_download_client.application.utils import get_iterable_days
from swps_tweet_download_client.domain.minio_credentials import MinioCredentials

_BUCKET_NAME = 'swps-twitter-data'
_CHUNK_SIZE = 1024 * 16


class MinioDownloader:
    _minio_credentials: MinioCredentials

    def __init__(self, minio_credentials: MinioCredentials):
        self._minio_credentials = minio_credentials

    def get_minio_client(self) -> Minio:
        return Minio(
            endpoint=self._minio_credentials.endpoint,
            access_key=self._minio_credentials.access_key,
            secret_key=self._minio_credentials.secret_key
        )

    @staticmethod
    def get_date_tag(date: Arrow) -> str:
        return date.isoformat()[:10]

    def provide_path(self, date: Arrow, phrase: str, root_directory: str) -> str:
        directory_path = os.path.join(root_directory, self.get_date_tag(date))
        pathlib.Path(directory_path).mkdir(parents=True, exist_ok=True)
        return os.path.join(directory_path, f'{phrase}.csv')

    def request_phrase_in_date(self, minio_path: str, save_path: str):
        response = self.get_minio_client().get_object(_BUCKET_NAME, minio_path)
        with open(save_path, 'wb') as out:
            while True:
                data = response.read(_CHUNK_SIZE)
                if not data:
                    break
                out.write(data)
        response.release_conn()

    def download_phrase_in_date(
            self,
            date: Arrow,
            phrase: str,
            root_directory: str
    ):
        date_str = date.isoformat()[:10]
        minio_path = f'tweets/{date_str}/{phrase}.csv'
        try:
            print(f'start download date: {date_str} phrase: {phrase}')
            self.request_phrase_in_date(minio_path, self.provide_path(date, phrase, root_directory))
            print(f'finish with success')
        except Exception as e:
            traceback.print_exc()
            print(e)
            print('Verify that object exists')

    def download_phrase_in_range(
            self,
            since: Arrow,
            until: Arrow,
            phrase: str,
            root_directory: str
    ):
        for date in get_iterable_days(since, until):
            self.download_phrase_in_date(date, phrase, root_directory)

    def download_phrases_in_range(
            self,
            since: Arrow,
            until: Arrow,
            phrases: List[str],
            root_directory: str
    ):
        for phrase in phrases:
            self.download_phrase_in_range(since, until, phrase, root_directory)
