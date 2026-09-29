import boto3
import os
from botocore.exceptions import ClientError
from botocore.exceptions import ClientError, NoCredentialsError
 
s3 = boto3.client("s3")
REGION = boto3.session.Session().region_name or "us-east-1"

#Create a bucket
def create_bucket():
    name = input("New bucket name: ").strip()
    try:
        if REGION == "us-east-1":
            s3.create_bucket(Bucket=name)
        else:
            s3.create_bucket(
                Bucket=name,
                CreateBucketConfiguration={"LocationConstraint": REGION},
            )
        print(f"Created bucket '{name}'")
    except ClientError as e:
        code = e.response["Error"]["Code"]
        if code == "BucketAlreadyExists":
            print("That name is taken by another AWS account.")
        elif code == "BucketAlreadyOwnedByYou":
            print("You already own that bucket.")
        else:
            print(f"[AWS ERROR] {code}")

#Buckets list
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
    

#Generate URL
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
    
    
#upload File
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

#download File 
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
            
            
#Delete Bucket
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
            
            
#backup folder
def backup_folder():
    folder = input("Local folder path: ").strip()
    bucket = input("Target bucket: ").strip()
    prefix = input("S3 prefix [backup/]: ").strip() or "backup/"

    # Vérifier que le dossier existe
    if not os.path.isdir(folder):
        print(f"Folder not found: {folder}")
        return

    # Ajouter un slash à la fin du préfixe
    if prefix and not prefix.endswith("/"):
        prefix += "/"

    successes = 0
    failures = 0

    print(f"\nStarting backup of: {folder}\n")

    for root, dirs, files in os.walk(folder):
        for filename in files:

            # Chemin absolu du fichier local
            local_path = os.path.join(root, filename)

            # Chemin relatif par rapport au dossier choisi
            relative = os.path.relpath(local_path, folder)

            # Construire la clé S3 en utilisant des slashs
            key = prefix + relative.replace(os.sep, "/")

            try:
                s3.upload_file(local_path, bucket, key)

                successes += 1
                print(f"[OK] {local_path} -> s3://{bucket}/{key}")

            except ClientError as e:
                failures += 1
                code = e.response["Error"]["Code"]
                print(f"[FAILED] {local_path} - {code}")

            except OSError as e:
                failures += 1
                print(f"[FAILED] {local_path} - {e}")

    print("\n========== BACKUP SUMMARY ==========")
    print(f"Successful uploads: {successes}")
    print(f"Failed uploads: {failures}")
    print(f"Total files: {successes + failures}")
    print("====================================")
    
    
# ==========================================
# MAIN MENU
# ==========================================

def display_menu():
    print("\n")
    print("=" * 43)
    print(" " * 14 + "S3 MANAGER")
    print("=" * 43)

    print("  1. Create Bucket       5. Download File")
    print("  2. List Buckets        6. Delete Bucket")
    print("  3. Upload File         7. Generate Presigned URL")
    print("  4. List Files          8. Backup Local Folder")
    print("  0. Exit")

    print("=" * 43)


def main():
    actions = {
        "1": create_bucket,
        "2": list_objects,
        "3": upload_file,
        "4": list_objects,
        "5": download_file,
        "6": delete_bucket,
        "7": generate_presigned_url,
        "8": backup_folder,
    }

    while True:
        display_menu()

        choice = input("\nChoose an option: ").strip()

        if choice == "0":
            print("\nThank you for using S3 Manager. Goodbye!")
            break

        action = actions.get(choice)

        if action:
            print()
            try:
                action()
            except NoCredentialsError:
                print(
                    "[ERROR] AWS credentials not found. "
                    "Please configure your AWS CLI."
                )
            except ClientError as e:
                print(f"[AWS ERROR] {e}")
            except Exception as e:
                print(f"[ERROR] {e}")

            input("\nPress Enter to return to the main menu...")

        else:
            print("[INVALID OPTION] Please choose a number between 0 and 9.")


# ==========================================
# APPLICATION ENTRY POINT
# ==========================================

if __name__ == "__main__":
    main()