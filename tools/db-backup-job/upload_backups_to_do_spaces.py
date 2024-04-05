import os
import boto3

region = os.getenv("REGION")
access_key_id = os.getenv("DO_SPACES_KEY")
access_key = os.getenv("DO_SPACES_SECRET")
do_spaces_bucket = os.getenv("DO_SPACES_BUCKET")
do_spaces_bucket_folder = os.getenv("DO_SPACES_BUCKET_FOLDER")

backup_local_path = os.getenv("BACKUP_LOCAL_PATH")
backup_name = os.getenv("BACKUP_NAME")

max_backups = int(os.environ.get("MAX_BACKUPS", "10"))

client = boto3.client('s3',
                      region_name=region,
                      endpoint_url=f'https://{region}.digitaloceanspaces.com',
                      aws_access_key_id=access_key_id,
                      aws_secret_access_key=access_key)

do_spaces_buckup_key = f"{do_spaces_bucket_folder}/{backup_name}"

print(f"Uploading {backup_local_path} to {do_spaces_buckup_key} on {do_spaces_bucket} space...")

client.upload_file(backup_local_path, do_spaces_bucket, do_spaces_buckup_key)

print("Backup uploaded to do spaces!")

print("Checking if we shouldn't remove old ones...")

backup_objects = client.list_objects_v2(Bucket=do_spaces_bucket, Prefix=do_spaces_bucket_folder).get("Contents", [])

sorted_backups = sorted(b['Key'] for b in backup_objects)

backups_to_delete = len(sorted_backups) - max_backups

if backups_to_delete >= max_backups:
    print(f"Deleting {backups_to_delete} backups...")
    
    to_delete_backups = sorted_backups[0:backups_to_delete]

    for b in to_delete_backups:
        print(f"Deleting {b} backup...")
        client.delete_object(Bucket=do_spaces_bucket, Key=b)

    print("Old backups deleted.")
else:
    print(f"There are less backups ({len(sorted_backups)}) than max allowed ({max_backups}), skipping deletion")