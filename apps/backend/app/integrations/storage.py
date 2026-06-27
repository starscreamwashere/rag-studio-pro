"""MinIO / S3-compatible object storage (boto3).

All functions are synchronous; async callers wrap them in a threadpool.
"""

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

from app.core.config import settings


def _client():
    return boto3.client(
        "s3",
        endpoint_url=settings.minio_endpoint,
        aws_access_key_id=settings.minio_root_user,
        aws_secret_access_key=settings.minio_root_password,
        region_name=settings.minio_region,
        config=Config(signature_version="s3v4"),
    )


def ensure_bucket(bucket: str) -> None:
    client = _client()
    try:
        client.head_bucket(Bucket=bucket)
    except ClientError:
        client.create_bucket(Bucket=bucket)


def upload_bytes(
    bucket: str, key: str, data: bytes, content_type: str = "application/octet-stream"
) -> None:
    ensure_bucket(bucket)
    _client().put_object(Bucket=bucket, Key=key, Body=data, ContentType=content_type)


def download_bytes(bucket: str, key: str) -> bytes:
    return _client().get_object(Bucket=bucket, Key=key)["Body"].read()


def delete_prefix(bucket: str, prefix: str) -> None:
    """Delete every object under a key prefix (used when a KB/document is removed)."""
    client = _client()
    paginator = client.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        objects = [{"Key": obj["Key"]} for obj in page.get("Contents", [])]
        if objects:
            client.delete_objects(Bucket=bucket, Delete={"Objects": objects})
