import os
import boto3

session = boto3.session.Session()
print(session)

region = os.getenv("REGION")
access_key_id = os.getenv("SPACES_KEY")
access_key = os.getenv("SPACES_SECRET")

client = session.client('s3',
                        region_name=region,
                        endpoint_url=f'https://{region}.digitaloceanspaces.com',
                        aws_access_key_id=access_key_id,
                        aws_secret_access_key=access_key)