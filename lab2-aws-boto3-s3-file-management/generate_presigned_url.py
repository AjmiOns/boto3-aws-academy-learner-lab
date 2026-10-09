# this script will generate a presigned url for an s3 object using boto3
import boto3
from botocore.exceptions import ClientError
 
s3 = boto3.client("s3")
REGION = boto3.session.Session().region_name or "us-east-1"

def generate_presigned_url():
    bucket  = input("Bucket name: ").strip()
    key     = input("Object key: ").strip()
    raw     = input("Valid for how many seconds? [3600]: ").strip()
    expires = int(raw) if raw.isdigit() else 3600
 
    url = s3.generate_presigned_url(
        ClientMethod="get_object",
        Params={"Bucket": bucket, "Key": key},
        ExpiresIn=expires,
    )
    print(f"\nValid for {expires} seconds:\n{url}\n")

generate_presigned_url()