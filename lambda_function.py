import json
import boto3
import os
from ec2 import EC2Utils
from github import GithubActions

def get_pat_token_from_ssm():
    return boto3.client('ssm').get_parameter(Name='github-actions-token-store')['Parameter']['Value']

def lambda_handler(event, context):
    sts = boto3.client('sts')
    role_arn = f"arn:aws:iam::{event['account_number']}:role/github-actions-lambda-ec2-role" # needs to be parameterized
    assumed_role = sts.assume_role(RoleArn=role_arn, RoleSessionName='session1')
    credentials = assumed_role['Credentials']
    
    org = event['org']
    pat = get_pat_token_from_ssm()
    
    ec2 = EC2Utils(credentials)
    gh = GithubActions(pat)
    token = gh.get_registration_token()['token']
    
    if event['mode'] == 'start':
        instance_data = ec2.start_instance(
            org=org,
            token=token,
            instance_type="t3.micro",
            subnet_id="subnet-04f62a30f30bcdba8",
            security_group_id="sg-017b884d399cfcbac",
            role_name="git-actions-self-hosted-ec2-instance-role"
        )
        return instance_data
        
    if event['mode'] == 'stop':
        gh.remove_runner(event['runner_label'])
        return ec2.terminate_instance(event['instance_id'])
