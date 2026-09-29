import boto3
from botocore.exceptions import ClientError

s3 = boto3.client("s3")
REGION = boto3.session.Session().region_name or "us-east-1"


def delete_bucket():
    bucket = input("Bucket name to delete: ").strip()

    confirmation = input(
        f"Type '{bucket}' to confirm deletion: "
    ).strip()

    if confirmation != bucket:
        print("Deletion cancelled.")
        return

    try:
        s3.delete_bucket(Bucket=bucket)
        print(f"Bucket '{bucket}' deleted successfully.")

    except ClientError as e:
        code = e.response["Error"]["Code"]

        if code == "BucketNotEmpty":
            print("Bucket is not empty. Delete all objects first.")

        elif code == "NoSuchBucket":
            print("Bucket does not exist.")

        else:
            print(f"[AWS ERROR] {code}")


delete_bucket()