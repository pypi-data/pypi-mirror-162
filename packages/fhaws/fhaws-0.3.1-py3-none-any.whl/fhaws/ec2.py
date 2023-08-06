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



def instance_inventory(profile, region=''):
    """get a CSV inventory of EC2 instances in AWS account. Inventories all regions unless a region is specified"""

    instances = {}
    if region:
        instances[region] = get_instances(profile, region)
    else:
        regions = [region for region in get_regions(profile)]
        for region in regions:
            instances[region] = get_instances(profile, region)

    inventory = ["InstanceId, Name, InstanceType, State, KeyName, Region, AvailabilityZone, PrivateIP, PublicIP, LaunchDate"]

    for region in instances:    
        for k in instances[region]:
            for i in k['Instances']:
                if 'PublicIpAddress' in i:
                    pub_ip = i['PublicIpAddress']
                else:
                    pub_ip = ''
                state = i['State']['Name']
                instanceid = i['InstanceId']
                instancetype = i['InstanceType']
                if "KeyName" in i:
                    keyname = i['KeyName']
                else:
                    keyname = ''
                priv_ip = i['PrivateIpAddress']
                az = i['Placement']['AvailabilityZone']
                launch_time = i['LaunchTime']
                name = ''
                for tag in i['Tags']:
                    if tag['Key'] == 'Name':
                        name = tag['Value']
                        continue

                inventory.append("%s, %s, %s, %s, %s, %s, %s, %s, %s, %s" % (instanceid, name, instancetype, state, keyname,
                                                                            region, az, priv_ip, pub_ip, launch_time))

    return("\n".join(inventory))

def get_regions(profile):
    """get availible AWS region names and endpoints"""
    session = boto3.Session(profile_name=profile)
    ec2 = session.client('ec2')
    response = ec2.describe_regions()
    regions = {}
    for region in response["Regions"]:
        regions[region["RegionName"]] = region["Endpoint"]
    
    return(regions)
