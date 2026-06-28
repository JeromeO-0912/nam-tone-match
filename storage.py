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