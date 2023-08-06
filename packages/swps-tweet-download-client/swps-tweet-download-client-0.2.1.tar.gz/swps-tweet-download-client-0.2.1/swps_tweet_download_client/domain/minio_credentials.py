from __future__ import annotations

from dataclasses import dataclass

from dynaconf import Dynaconf


@dataclass
class MinioCredentials:
    endpoint: str
    access_key: str
    secret_key: str

    @classmethod
    def from_config(cls, dynaconf: Dynaconf) -> MinioCredentials:
        return cls(
            endpoint=dynaconf.minio.endpoint,
            access_key=dynaconf.minio.access_key,
            secret_key=dynaconf.minio.secret_key,
        )
