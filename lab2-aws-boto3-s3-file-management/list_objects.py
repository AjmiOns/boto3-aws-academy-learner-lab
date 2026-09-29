import boto3
from botocore.exceptions import ClientError
 
s3 = boto3.client("s3")
REGION = boto3.session.Session().region_name or "us-east-1"

def list_objects():
    bucket = input("Bucket name: ").strip()
    prefix = input("Prefix filter (Enter for all): ").strip()
 
    paginator = s3.get_paginator("list_objects_v2")
    pages = paginator.paginate(Bucket=bucket, Prefix=prefix)
 
    total_objects = 0
    total_bytes = 0
 
    for page in pages:
        for obj in page.get("Contents", []):
            total_objects += 1
            total_bytes += obj["Size"]
            print(f"{obj['Key']:<50} {obj['Size']:>12,}  "
                  f"{obj['LastModified']:%Y-%m-%d %H:%M}")
 
    print(f"\n{total_objects} object(s), "
          f"{total_bytes / 1024 / 1024:.2f} MB")
list_objects()