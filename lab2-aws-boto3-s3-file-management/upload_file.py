import os
import boto3
from botocore.exceptions import ClientError
 
s3 = boto3.client("s3")
REGION = boto3.session.Session().region_name or "us-east-1"

def upload_file():
    path   = input("Local file path: ").strip()
    bucket = input("Target bucket: ").strip()
 
    if not os.path.isfile(path):
        print(f"File not found: {path}")
        return
 
    default_key = os.path.basename(path)
    key = input(f"Object key [{default_key}]: ").strip() or default_key
 
    s3.upload_file(path, bucket, key)
    print(f"Uploaded {path} -> s3://{bucket}/{key}")


upload_file()