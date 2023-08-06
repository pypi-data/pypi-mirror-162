import boto3

def getaccounts(profile):
    session = boto3.Session(profile_name=profile)
    client = session.client("organizations")
    Accounts = client.list_accounts()
    all_accounts = []

    accounts = Accounts["Accounts"]

    while "NextToken" in Accounts:
        Accounts = client.list_accounts(NextToken=Accounts["NextToken"])
        accounts.extend(Accounts["Accounts"])
    
    for account in accounts:
        all_accounts.append(account)

    return(all_accounts)


def account_inventory(profile):
    accounts = getaccounts(profile)
    inventory = ["Name, ID, Email, ARN, Status, JoinedMethod, JoinedTimestamp"]
    for account in accounts:
        Id = account['Id']
        Arn = account['Arn']
        Email = account['Email']
        Name = account['Name']
        Status = account['Status']
        JoinedMethod = account['JoinedMethod']
        JoinedTimestamp = account['JoinedTimestamp']
        inventory.append("%s, %s, %s, %s, %s, %s, %s"  % (Name, Id, Email, Arn, Status, JoinedMethod, JoinedTimestamp))

    return('\n'.join(inventory))


def getorg(profile):
    session = boto3.Session(profile_name=profile)
    client = session.client("organizations")
    org  = client.describe_organization()
    orginfo = org["Organization"]

    return(orginfo)

def getroots(profile):
    session = boto3.Session(profile_name=profile)
    client = session.client("organizations")
    Roots = client.list_roots()
    roots = Roots['Roots']
    all_roots = []

    for root in roots:
        all_roots.append(root)

    return(all_roots)


def getous(profile, parent):
    # needs NextToken pagination
    session = boto3.Session(profile_name=profile)
    client = session.client("organizations")
    OUs = client.list_organizational_units_for_parent(ParentId=parent)
    ous = OUs['OrganizationalUnits']

    return(ous)       

def getchildren(profile, parent, child_type):
    # Child types are 'ACCOUNT' or 'ORGANIZATIONAL_UNIT'
    session = boto3.Session(profile_name=profile)
    client = session.client("organizations")
    response = client.list_children(ParentId=parent, ChildType=child_type)

    all_children = response["Children"]

    while "NextToken" in response:
        response = client.list_children(ParentId=parent, ChildType=child_type, NextToken=response["NextToken"])
        all_children.extend(response["Children"])

    return(all_children)


def account_name_lookup(profile):
    """Generate account ID to Name lookup table"""
    accounts = getaccounts(profile)
    map = {}
    for account in accounts:
        map[account['Id']] = account['Name']
    return(map)


def org_structure(profile):
    """Returns an ou to account dictionary"""
    root = getroots(profile)[0]['Id']
    lookup = account_name_lookup(profile)
    ous = getous(profile, root)
    s = {}
    for ou in ous:
        children = getchildren(profile, ou['Id'], 'ACCOUNT')
        c = []
        for child in children:
            c.append(lookup[child['Id']])
        s[ou['Name']] = c
    return(s)


def org_diagram(profile):
    """Generate a Mermiad formated organization diagram"""
    org = getorg("hdc-aws")
    org_name = org["MasterAccountEmail"].split("@")[0].upper()
    org_id = org["MasterAccountId"]
    structure = org_structure(profile)
    chart = ["flowchart TB"]
    chart.append("Root(((\"%s\\n%s\")))" % (org_name, org_id))
    for ou in structure:
        chart.append("Root --> %s[/%s\\]" % (ou.lower(), ou.upper()))
        prev = ''
        accts = structure[ou]
        n = 15
        if len(accts) > n:
            chunks = [accts[i:i+n] for i in range(0, len(accts), n)]
            for chunk in chunks:
                for acct in chunk:
                    if not prev:
                        chart.append("%s --> %s" % (ou.lower(), acct.lower()))
                    else:
                        chart.append("%s --> %s" % (prev.lower(), acct.lower()))
                    prev = acct.lower()
                prev = ""

        else:
            for acct in structure[ou]:
                if not prev:
                    chart.append("%s --> %s" % (ou.lower(), acct.lower()))
                else:
                    chart.append("%s --> %s" % (prev.lower(), acct.lower()))
                prev = acct.lower()
    return("\n".join(chart))



if __name__ == "__main__":
    import sys
    profile = sys.argv[1]
    print(getorg(profile))
    

