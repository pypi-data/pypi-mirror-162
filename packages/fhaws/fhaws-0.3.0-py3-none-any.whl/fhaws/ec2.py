import boto3

def get_instances(profile, region):
    """get_users returns a list of all EC2 instances in the account"""
    """need to add logic to get all regions, if region not provided"""
    session = boto3.Session(profile_name=profile, region_name=region)
    client = session.client("ec2")
    response = client.describe_instances()

    all_instances = []

    instances = response["Reservations"]

    while "NextToken" in instances:
        instances = client.describe_instances(NextToken=response["NextToken"])
        instances.extend(instances["Reservations"])
    
    for instance in instances:
        all_instances.append(instance)

    return(all_instances)

def get_regions(profile):
    """get availible AWS region names and endpoints"""
    session = boto3.Session(profile_name=profile)
    ec2 = session.client('ec2')
    response = ec2.describe_regions()
    regions = {}
    for region in response["Regions"]:
        regions[region["RegionName"]] = region["Endpoint"]
    
    return(regions)
    