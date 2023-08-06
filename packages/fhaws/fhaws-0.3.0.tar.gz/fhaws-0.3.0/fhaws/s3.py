import boto3

def get_buckets(profile):
    session = boto3.Session(profile_name=profile)
    client = session.client("s3")
    response = client.list_buckets()

    for bucket in response['Buckets']:
        print(f'  {bucket["Name"]}')