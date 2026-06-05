# multi_account.py
import boto3

ACCOUNTS = [
    {"id": "515206814398", "name": "personal"},
    {"id": "582596730397", "name": "staging"},
]

def get_session_for_account(account_id, account_name):

    # Personal account — use direct credentials, no role needed
    if account_id == "515206814398":
        return boto3.Session(region_name='ap-south-1')

    # Staging — use STS AssumeRole
    sts = boto3.client('sts')
    assumed = sts.assume_role(
        RoleArn=f'arn:aws:iam::{account_id}:role/CloudWiseScanner',
        RoleSessionName=f'CloudWise-{account_name}'
    )
    creds = assumed['Credentials']
    return boto3.Session(
        aws_access_key_id=creds['AccessKeyId'],
        aws_secret_access_key=creds['SecretAccessKey'],
        aws_session_token=creds['SessionToken'],
        region_name='ap-south-1'
    )
