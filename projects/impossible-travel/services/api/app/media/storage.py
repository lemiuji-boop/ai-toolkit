# Copyright 2026 Rinat Ishmaev
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Хранилище ассетов в MinIO/S3."""

import logging

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

from app.core.config import Settings, get_settings

logger = logging.getLogger(__name__)


class AssetStorage:
    """Обёртка над S3-compatible storage."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self._client = boto3.client(
            "s3",
            endpoint_url=self.settings.s3_endpoint,
            aws_access_key_id=self.settings.s3_access_key,
            aws_secret_access_key=self.settings.s3_secret_key,
            region_name=self.settings.s3_region,
            config=Config(signature_version="s3v4"),
        )
        self._ensure_bucket()

    def _ensure_bucket(self) -> None:
        """Создаёт bucket если не существует."""
        bucket = self.settings.s3_bucket
        try:
            self._client.head_bucket(Bucket=bucket)
        except ClientError:
            try:
                self._client.create_bucket(Bucket=bucket)
                logger.info("Created bucket %s", bucket)
            except ClientError as exc:
                logger.warning("Could not create bucket: %s", exc)

    async def upload_bytes(self, key: str, data: bytes, content_type: str) -> str:
        """Загружает файл и возвращает публичный URL."""
        bucket = self.settings.s3_bucket
        self._client.put_object(
            Bucket=bucket,
            Key=key,
            Body=data,
            ContentType=content_type,
        )
        return f"{self.settings.s3_endpoint}/{bucket}/{key}"
