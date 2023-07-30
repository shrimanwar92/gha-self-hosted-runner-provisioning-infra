import json
import boto3
import string
import random
from ec2 import EC2Utils
from github import GithubActions

org = "taviscasolutions-poc"

def get_pat_token_from_ssm(repo_name):
    client = boto3.client("ssm", region_name = "us-east-1")
    response = json.loads(client.get_parameter(Name = "BnR-github-actions-product-repo-pat-poc")['Parameter']['Value'])
    return response[repo_name]

def generate_label():
    #initializing size of string
    N = 7

    # using random.choices()
    # generating random strings
    random_string = ''.join(random.choices(string.ascii_lowercase +string.digits, k=N))
    return str(random_string)

def get_lambda_config(function_name):
    lambda_client = boto3.client('lambda')
    config = lambda_client.get_function_configuration(
        FunctionName = function_name
    )
    return {
        "vpc_id": config['VpcConfig']['VpcId'],
        "subnet_id": config['VpcConfig']['SubnetIds'][0],
        "security_group_id": config['VpcConfig']['SecurityGroupIds'][0]
    }

def lambda_handler(event, context):
    config = get_lambda_config(context.function_name)
    label = generate_label()
    
    repo = event['repo']
    pat = get_pat_token_from_ssm(repo)
    
    ec2 = EC2Utils()
    gha = GithubActions(org, repo, pat)
    token = gha.get_registration_token()['token']
    
    if event['mode'] == 'start':
        print("Instance creation starting...")
        instance_data = ec2.start_instance(
            org = org,
            repo = repo,
            token = token,
            ami_id = "ami-0e2a0b6f2846273f6",
            instance_type = "t3.medium",
            subnet_id = config['subnet_id'], #"subnet-04c8a1cce0a80f526",
            security_group_id = config['security_group_id'], #security_group_id,
            role_name = "ec2-self-hosted-runner-gha-job-role",
            label = label
        )
        gha.wait_for_runner_registration(label)
        return instance_data
        
    if event['mode'] == 'stop':
        gha.remove_runner(event['runner_label'])
        return ec2.terminate_instance(event['instance_id'])
