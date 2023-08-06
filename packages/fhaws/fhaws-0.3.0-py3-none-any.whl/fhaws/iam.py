from curses.ascii import US
from re import A
import boto3

def get_users(profile):
    """get_users returns a list of all IAM user objects in the accounts"""
    session = boto3.Session(profile_name=profile)
    client = session.client("iam")
    response = client.list_users()

    all_users = []

    users = response["Users"]

    while response["IsTruncated"]:
    #while "Marker" in response: # this works too
        response = client.list_users(Marker=response["Marker"])
        users.extend(response["Users"])
    
    for user in users:
        all_users.append(user)
    
    return(all_users)


def inventory_users(profile):
    """inventory_users returns a CSV of IAM users"""
    # need to add info about API keys and MFAs
    users = get_users(profile)
    inventory = ["UserName, UserId, Arn, CreateDate, PasswordLastUsed"]
    for u in users:
        username = u["UserName"]
        id = u["UserId"]
        arn = u["Arn"]
        cdate = u["CreateDate"]
        try:
            pdate = u["PasswordLastUsed"]
        except:
            pdate = "Never"
        inventory.append("%s, %s, %s, %s, %s" % (username, id, arn, cdate, pdate))

    return("\n".join(inventory))


def get_mfas(profile):
    "return a list of all MFA objects in the AWS account"
    session = boto3.Session(profile_name=profile)
    client = session.client("iam")
    response = client.list_virtual_mfa_devices()
    mfas = response["VirtualMFADevices"]

    while response["IsTruncated"]:
        response = client.list_virtual_mfa_devices(Marker=response["Marker"], MaxItems=2)
        mfas.extend(response["VirtualMFADevices"])
    
    return(mfas)
    

def get_access_keys(profile, username=''):
    """return a list of access keys for a specific users, or all access_keys"""
    session = boto3.Session(profile_name=profile)
    client = session.client("iam")
    access_keys = []
    if username:
        response = client.list_access_keys(UserName=username)
        if "AccessKeyMetadata" in response:
            access_keys.append(response["AccessKeyMetadata"])
    else:
        usernames = [user['UserName'] for user in get_users(profile)]
        for user in usernames:
            response = client.list_access_keys(UserName=user)
            if "AccessKeyMetadata" in response:
                access_keys.extend(response["AccessKeyMetadata"])
    
    return(access_keys)


def get_ssh_keys():
    pass

if __name__ == "__main__":
    import sys
    profile = sys.argv[1]
    print(inventory_users(profile))

