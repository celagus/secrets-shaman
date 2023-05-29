import boto3
import sys
sys.path.append('../app')
from modules.shaman_config import *
import base64
import re
import json

def assume_role(role_name):
    sts_client = boto3.client('sts')
    assumed_role_object = sts_client.assume_role(
        RoleArn=role_name,
        RoleSessionName="AssumeRoleSession"
    )
    return assumed_role_object['Credentials']

def get_org_accounts() -> list:
    credentials = assume_role(f"arn:aws:iam::{ORG_ACCOUNT_ID}:role/{SHAMAN_ROLE_NAME}")
    org_client = boto3.client('organizations',
        aws_access_key_id=credentials['AccessKeyId'],
        aws_secret_access_key=credentials['SecretAccessKey'],
        aws_session_token=credentials['SessionToken']
    )
    accounts = org_client.list_accounts()
    return accounts

def get_secrets_from_lambda_env(credentials, region) -> list:
    lambda_client = boto3.client(
        'lambda',
        region_name=region,
        aws_access_key_id=credentials['AccessKeyId'],
        aws_secret_access_key=credentials['SecretAccessKey'],
        aws_session_token=credentials['SessionToken']
    )
    paginator = lambda_client.get_paginator('list_functions')
    page_iterator = paginator.paginate()
    lambda_list = []
    for page in page_iterator:
        for function in page['Functions']:
            response = lambda_client.get_function(
                FunctionName=function['FunctionName']
            )
            if "Environment" in response['Configuration'].keys():
                js = json.dumps(response['Configuration']['Environment']['Variables'])
                if re.findall(POWER_REGEX, js):
                    lambda_list.append({
                        "asset": function['FunctionName'],
                        "asset_type": "AwsLambdaFunction",
                        "finding": "possible secret in environment variables"
                    })
                    print(f"Possible secret detected in {function['FunctionName']}")
    return lambda_list

def get_secrets_from_user_data_env(credentials, region) -> list:
    ec2_client = boto3.client(
        'ec2',
        region_name=region,
        aws_access_key_id=credentials['AccessKeyId'],
        aws_secret_access_key=credentials['SecretAccessKey'],
        aws_session_token=credentials['SessionToken']
    )
    paginator = ec2_client.get_paginator('describe_instances')
    page_iterator = paginator.paginate()
    # Create a list to hold the instance metadata
    instance_user_data = []
    # Iterate over each page of instance data and add it to the list
    for page in page_iterator:
        for reservation in page['Reservations']:
            for instance in reservation['Instances']:
                response = ec2_client.describe_instance_attribute(
                    Attribute='userData',
                    InstanceId=instance['InstanceId']
                )
                if "Value" in response['UserData'].keys():
                    if re.match(POWER_REGEX, str(base64.b64decode(response['UserData']['Value']).decode('utf-8'))):
                        print(f"Possible secret detected in {instance['InstanceId']}")
                        instance_user_data.append({
                            "asset": instance['InstanceId'],
                             "asset_type": "AwsEc2Instance",
                             "finding": "possible secret in user-data"
                        })
    return instance_user_data
