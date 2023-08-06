# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fhaws']

package_data = \
{'': ['*']}

install_requires = \
['boto3>=1.24.37,<2.0.0']

setup_kwargs = {
    'name': 'fhaws',
    'version': '0.3.0',
    'description': 'A module containing helper functions to make working with Boto3 and Amazon AWS easier with Python',
    'long_description': '# FHAWS\n\nHelper functions to make working with Boto3 and AWS easier via Python\n## Organizations\n\nA collections of functions for AWS Organizations\n\nExample diagram created by the "org_diagram" function:\n\n![Example Organization Diagram](/images/example-org-diagram-1.png)\n\n\n```python\nimport fhaws.org as org\n```\n\n**Available Functions**\n\n### **getaccounts(profile)**\n\n\nReturns a dictionary of all AWS accounts that are members of the organization.\n\nRequired parameters:\n\n1. profile:  the name of the AWS profile to use\n\n\n### **account_inventory(profile)**\n\nReturns a CSV report, including all available information on all AWS accounts that are members of the AWS Organization.\n\nRequired parameters:\n\n1. profile:  the name of the AWS profile to use\n\nProvided fields:\n\n- Name\n- Id\n- Email\n- Arn\n- Status\n- JoinedMethod\n- JoinedTimestamp\n\n\n### **getorg(profile)**\n\nGet information about the organization \n\nRequired parameters:\n\n1. profile:  the name of the AWS profile to use\n\n### **getroots(profile)**\n\nGet information about the root of the organization\n\nRequired parameters:\n\n1. profile:  the name of the AWS profile to use\n\n### **getous(profile, parent)**\n\nGet the OUs directly under the specified parent (root or parent OU)\n\nRequired parameters:\n\n1. profile: the name of the AWS profile to use\n2. parent: the id of the parent object\n\n### **getchildren(profile, parent, child_type)**\n\nGet the children objects under the parent. you must also specify the type of children you want "\n\nRequired parameters:\n\n1. profile: the name of the AWS profile to use\n2. parent: the id of the parent object\n3. child_type: the type of child objects you want (\'ACCOUNT\' or \'ORGANIZATIONAL_UNIT\')\n\n### **account_name_lookup(profile)**\n\nGenerate a account Id to Name lookup dictionary\n\nRequired parameters:\n\n1. profile: the name of the AWS profile to use\n\n### **org_structure(profile)**\n\nGenerate an dictionary containing the structure of the organization. OUs are Keys with a list of the children accounts as the value.\n\nRequired parameters:\n\n1. profile: the name of the AWS profile to use\n\n### **org_diagram(profile)**\n\nGenerate a mermaid formatted diagram of the organizational structure, similar to the example diagram at the top of the Organziations section above.\n\nRequired parameters:\n\n1. profile: the name of the AWS profile to use\n\n## IAM\n\nA collection for working with AWS IAM \n\n```python\nimport fhaws.iam as iam\n```\n\n### **get_users(profile)**\n\nGet all IAM user objects in the AWS account\n\n\n### **inventory_users(profile)**\n\nGet a CSV inventory of all IAM users in the AWS account\n\n\n### **get_mfas(profile)**\n\nGet a list of MFA objects for an entire AWS account\n\n\n### **get_access_keys(profile, username=\'\')**\n\nGet information on the access keys for a single user is a username is provided, or information all all access keys in the AWS account if the username is omitted.\n\n\nExample combining the fhaws.iam.get_users() and fhaws.iam.get_access_keys() functions to create a simple access keys report for an AWS account:\n\n```python\nimport fhaws.iam as iam\nprofile = \'aws-profile2\'\naccess_keys = iam.get_access_keys(profile)\nusernames = [user[\'UserName\'] for user in iam.get_users(profile)]\nprint("UserName, AccessKeyId, Status, CreateData")\nfor user in usernames:\n    for key in access_keys:\n        if key[\'UserName\'] == user:\n            print("%s: %s, %s, %s" % (user, key[\'AccessKeyId\'],\n                                     key[\'Status\'], key[\'CreateDate\']))\n```\n\nOutput:\n\n```\nUserName, AccessKeyId,         Status,   CreateDate\nuser1:    AXAXYCYGMXZWTDFAKE,  Active,   2022-04-05 19:48:19+00:00\nuser2:    AXAXYCYGMXZSZGFAKE,  Inactive, 2021-11-08 20:06:20+00:00\nuser3:    AXAXYCYGMXZXHKFAKE,  Active,   2022-07-01 00:43:46+00:00\nuser4:    AXAXYCYGMXZTO3FAKE,  Active,   2021-10-19 17:27:41+00:00\nuser5:    AXAXYCYGMXZ2PLFAKE,  Active,   2022-07-22 21:49:52+00:00\nuser6:    AXAXYCYGMXZ4J3FAKE,  Active,   2022-07-14 15:41:14+00:00\n...\n```\n\n\n## S3\n\nFuture\n\n## EC2\n\nFuture\n\n',
    'author': 'Robert McDermott',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/robert-mcdermott/fhaws',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
