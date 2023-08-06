# FHAWS

Helper functions to make working with Boto3 and AWS easier via Python
## Organizations

A collections of functions for AWS Organizations

Example diagram created by the "org_diagram" function:

![Example Organization Diagram](/images/example-org-diagram-1.png)


```python
import fhaws.org as org
```

**Available Functions**

### **getaccounts(profile)**


Returns a dictionary of all AWS accounts that are members of the organization.

Required parameters:

1. profile:  the name of the AWS profile to use


### **account_inventory(profile)**

Returns a CSV report, including all available information on all AWS accounts that are members of the AWS Organization.

Required parameters:

1. profile:  the name of the AWS profile to use

Provided fields:

- Name
- Id
- Email
- Arn
- Status
- JoinedMethod
- JoinedTimestamp


### **getorg(profile)**

Get information about the organization 

Required parameters:

1. profile:  the name of the AWS profile to use

### **getroots(profile)**

Get information about the root of the organization

Required parameters:

1. profile:  the name of the AWS profile to use

### **getous(profile, parent)**

Get the OUs directly under the specified parent (root or parent OU)

Required parameters:

1. profile: the name of the AWS profile to use
2. parent: the id of the parent object

### **getchildren(profile, parent, child_type)**

Get the children objects under the parent. you must also specify the type of children you want "

Required parameters:

1. profile: the name of the AWS profile to use
2. parent: the id of the parent object
3. child_type: the type of child objects you want ('ACCOUNT' or 'ORGANIZATIONAL_UNIT')

### **account_name_lookup(profile)**

Generate a account Id to Name lookup dictionary

Required parameters:

1. profile: the name of the AWS profile to use

### **org_structure(profile)**

Generate an dictionary containing the structure of the organization. OUs are Keys with a list of the children accounts as the value.

Required parameters:

1. profile: the name of the AWS profile to use

### **org_diagram(profile)**

Generate a mermaid formatted diagram of the organizational structure, similar to the example diagram at the top of the Organziations section above.

Required parameters:

1. profile: the name of the AWS profile to use

## IAM

A collection for working with AWS IAM 

```python
import fhaws.iam as iam
```

### **get_users(profile)**

Get all IAM user objects in the AWS account


### **inventory_users(profile)**

Get a CSV inventory of all IAM users in the AWS account


### **get_mfas(profile)**

Get a list of MFA objects for an entire AWS account


### **get_access_keys(profile, username='')**

Get information on the access keys for a single user is a username is provided, or information for all access keys in the AWS account if the username is omitted.


Example combining the **fhaws.iam.get_users()** and **fhaws.iam.get_access_keys()** functions to create a simple access keys report for an AWS account:

```python
import fhaws.iam as iam
profile = 'aws-profile2'
access_keys = iam.get_access_keys(profile)
usernames = [user['UserName'] for user in iam.get_users(profile)]
print("UserName, AccessKeyId, Status, CreateDate")
for user in usernames:
    for key in access_keys:
        if key['UserName'] == user:
            print("%s: %s, %s, %s" % (user, key['AccessKeyId'],
                                     key['Status'], key['CreateDate']))
```

Output:

```
UserName, AccessKeyId,         Status,   CreateDate
user1:    AXAXYCYGMXZWTDFAKE,  Active,   2022-04-05 19:48:19+00:00
user2:    AXAXYCYGMXZSZGFAKE,  Inactive, 2021-11-08 20:06:20+00:00
user3:    AXAXYCYGMXZXHKFAKE,  Active,   2022-07-01 00:43:46+00:00
user4:    AXAXYCYGMXZTO3FAKE,  Active,   2021-10-19 17:27:41+00:00
user5:    AXAXYCYGMXZ2PLFAKE,  Active,   2022-07-22 21:49:52+00:00
user6:    AXAXYCYGMXZ4J3FAKE,  Active,   2022-07-14 15:41:14+00:00
...
```


## S3

### **get_buckets(profile)**

Returns a list of all S3 buckets in the AWS account.
## EC2

### **get_regions(profile)**

Returns a dictionary of all AWS regions in the form of "RegionName = EndpointURL"

### **instance_inventory(profile, region='')**

Generates a simple (need to add more fields) CSV report on the EC2 instances in an account. By default it will look for EC2 instances in all AWS regions around the globe. You can optionally provide a region to restrict the inventory to a specific region.


