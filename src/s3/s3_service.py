import logging
from contextlib import asynccontextmanager
from typing import Optional

from botocore.exceptions import ClientError
from types_aiobotocore_s3.client import S3Client
from aiobotocore.session import get_session, AioSession

from src.settings import settings


class S3Service:

    config: Optional[dict] = None
    bucket_name: Optional[str] = None
    session: Optional[AioSession] = None

    @classmethod
    async def init_s3(
            cls,
            bucket_name: str,
            endpoint_url: str,
            external_url: str,
            access_key: str,
            secret_key: str,
    ) -> None:

        if cls.session is not None:
            print("S3 is already initialized")
            return
        cls.external_url = external_url
        cls.config = {
            "aws_access_key_id": access_key,
            "aws_secret_access_key": secret_key,
            "endpoint_url": endpoint_url
        }
        cls.bucket_name = bucket_name
        cls.session = get_session()
        logging.info("S3 initialized")

    @classmethod
    async def close_s3(cls) -> None:
        if cls.session is None:
            print("S3 is already closed")
            return
        cls.bucket_name = None
        cls.config = None
        cls.session = None

    @classmethod
    @asynccontextmanager
    async def get_client(cls):
        async with cls.session.create_client("s3", **cls.config) as client:
            yield client

    @classmethod
    async def upload_file_object(cls, object_name, content) -> str:
        async with cls.get_client() as client:
            client: S3Client
            await client.put_object(Bucket=cls.bucket_name, Key=object_name, Body=content)
            return f"{cls.external_url}/{cls.bucket_name}/{object_name}"

    @classmethod
    async def get_file_object(cls, object_name) -> Optional[bytes]:
        async with cls.get_client() as client:
            client: S3Client

            try:
                resp = await client.get_object(Bucket=cls.bucket_name, Key=object_name)
            except ClientError as e:
                if e.response["Error"]["Code"] == "NoSuchKey":
                    logging.info("No object found")
                    return
                else:
                    raise

            async with resp["Body"] as stream:
                data = await stream.read()
            return data

    @classmethod
    async def delete_file_object(cls, object_name) -> None:
        async with cls.get_client() as client:
            client: S3Client
            await client.delete_object(Bucket=cls.bucket_name, Key=object_name)


