import os
import boto3
from dotenv import load_dotenv

load_dotenv()

s3 = boto3.client(
    "s3",
    endpoint_url=os.getenv("S3_ENDPOINT_URL"),
    aws_access_key_id=os.getenv("S3_ACCESS_KEY"),
    aws_secret_access_key=os.getenv("S3_SECRET_KEY")
)

BUCKET = os.getenv("S3_BUCKET")

def upload_fileobj(fileobj, key, content_type=None):
    extra = {"ContentType": content_type} if content_type else {}
    s3.upload_fileobj(fileobj, BUCKET, key, ExtraArgs=extra)
    return key

def download_file(key, local_path):
    s3.download_file(BUCKET, key, local_path)

def upload_file(file_path, key, content_type=None):
    extra = {"ContentType": content_type} if content_type else {}
    s3.upload_file(file_path, BUCKET, key, ExtraArgs=extra)
    return key

def get_object_bytes(key):
    response = s3.get_object(Bucket=BUCKET, Key=key)
    return response['Body'].read()