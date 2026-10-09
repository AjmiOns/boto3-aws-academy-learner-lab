# this script will backup a local folder to an s3 bucket using boto3
import boto3
import os
from botocore.exceptions import ClientError

s3 = boto3.client("s3")
REGION = boto3.session.Session().region_name or "us-east-1"

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

backup_folder()