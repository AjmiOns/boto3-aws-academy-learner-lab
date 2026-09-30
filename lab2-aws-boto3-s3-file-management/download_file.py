# this script will download a file from an s3 bucket using boto3
import boto3
from botocore.exceptions import ClientError
 
s3 = boto3.client("s3")
REGION = boto3.session.Session().region_name or "us-east-1"

def download_file():
    bucket = input("Bucket name: ").strip()
    key    = input("Object key: ").strip()
    dest   = input("Save as: ").strip() or os.path.basename(key)
 
    try:
        s3.download_file(bucket, key, dest)
        print(f"Downloaded -> {dest}")
    except ClientError as e:
        if e.response["Error"]["Code"] == "404":
            print("That object does not exist.")
        else:
            raise
download_file()