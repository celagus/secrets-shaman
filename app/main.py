import sys
import json
sys.path.append('../app')
from modules.aws import *
from modules.shaman_config import REGIONS

findings = []

def shaman():
    accounts = get_org_accounts()
    for account in accounts['Accounts']:
        for region in REGIONS:
            account_id = account['Id']
            print(f"Processing account: {account_id} region: {region}")
            credentials = assume_role(f"arn:aws:iam::{account_id}:role/{SHAMAN_ROLE_NAME}")
            findings.extend(get_secrets_from_lambda_env(credentials, region))
            findings.extend(get_secrets_from_user_data_env(credentials, region))

if __name__ == '__main__':
    print("*** Starting Secret's Shaman ***")
    shaman()
    print(f"*** Resources with possible secrets detected: {len(findings)} ***")
    if len(findings) > 0:
        print("*** Results ***")
        print(json.dumps(findings, indent=2))
