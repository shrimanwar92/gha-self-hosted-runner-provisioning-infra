# import json
# import botocore
# from os import environ
# import time
# import boto3
# import urllib.request
# import time
 
# ssm_client = boto3.client('ssm', region_name='us-east-1')
 
# def lambda_handler(event, context):
    
#     try:
#         instance_id = ssm_client.get_parameter(Name='MongoDbInstance')['Parameter']['Value']
#         doc_name = "mongodb-backup-document"
#         response = ssm_client.send_command(
#             DocumentName=doc_name, 
#             InstanceIds=[instance_id],
#             CloudWatchOutputConfig={
#                 'CloudWatchLogGroupName': context.log_group_name,
#                 'CloudWatchOutputEnabled': True
#             },
#         )
#         print(response)
    
#     except Exception as e:
#         raise e
#     else:
#         time.sleep(3)
#         response1 = ssm_client.get_command_invocation(
#             CommandId=response['Command']['CommandId'],
#             InstanceId=instance_id
#         )
#         return {
#             'statusCode': 200,
#             'body': json.dumps(response1, indent=4, sort_keys=True, default=str)
#         }

#  sudo yum update -y && \
#  sudo yum install docker -y && \
#  sudo yum install git -y && \
#  sudo yum install libicu -y && \
#  sudo systemctl enable docker

# need this in nilays account so that nilay's account can assume archanas account role

# {
#     "Action": "sts:AssumeRole",
#     "Resource": [
#         "arn:aws:iam::535190322927:role/github-actions-lambda-ec2-role",
#         "arn:aws:iam::535190322927:role/github-actions-lambda-ec2-role/*"
#     ],
#     "Effect": "Allow"
# }

# in archanas account i need to set proper trust relationship









import json
import boto3
from ec2 import EC2Utils
from github import GithubActions

org = "taviscasolutions-poc"

def get_pat_token_from_ssm(repo_name):
    client = boto3.client("ssm", region_name = "us-east-1")
    response = json.loads(client.get_parameter(Name = "BnR-github-actions-product-repo-pat-poc")['Parameter']['Value'])
    return response[repo_name]

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
    #aws_account_id = context.invoked_function_arn.split(":")[4]
    config = get_lambda_config(context.function_name)
    #vpc_id = "vpc-07b12bcec12a4cd9b"
    #security_group_id = "sg-044a84c760e77fd96" #make sure the sg is created in same vpc as that of subnet to launch ec2
    #sts = boto3.client('sts')
    #role_arn = f"arn:aws:iam::{aws_account_id}:role/azfootprint-role" # needs to be parameterized
    #assumed_role = sts.assume_role(RoleArn=role_arn, RoleSessionName='session1')
    #credentials = assumed_role['Credentials']
    
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
            role_name = "ec2-self-hosted-runner-gha-job-role"
        )
        return instance_data
        
    if event['mode'] == 'stop':
        gha.remove_runner(event['runner_label'])
        return ec2.terminate_instance(event['instance_id'])











import string
import random
import boto3
import json
import botocore
from typing import TypedDict
import sys

class InstanceOptions(TypedDict):
    org: str
    repo: str
    token: str
    ami_id: str
    instance_type: str
    subnet_id: str
    security_group_id: str
    role_name: str


class EC2Utils():
    def __init__(self) -> None:
        self.client = boto3.client(
            'ec2',
            #aws_access_key_id=credentials['AccessKeyId'],
            #aws_secret_access_key=credentials['SecretAccessKey'],
            #aws_session_token=credentials['SessionToken']
        )

    def generate_label(self):
        #initializing size of string
        N = 7
 
        # using random.choices()
        # generating random strings
        random_string = ''.join(random.choices(string.ascii_lowercase +string.digits, k=N))
        return str(random_string)
        
    def start_instance(self, **opts: InstanceOptions):
        label = self.generate_label()
        print(f"Runner label: {label}")
        
        user_data = "\n".join([
            "#!/bin/bash",
            "mkdir -p actions-runner && cd actions-runner",
            "case $(uname -m) in aarch64) ARCH='arm64' ;; amd64|x86_64) ARCH='x64' ;; esac && export RUNNER_ARCH=${ARCH}",
            "curl -O -L https://github.com/actions/runner/releases/download/v2.299.1/actions-runner-linux-${RUNNER_ARCH}-2.299.1.tar.gz",
            "tar xzf ./actions-runner-linux-${RUNNER_ARCH}-2.299.1.tar.gz",
            "export RUNNER_ALLOW_RUNASROOT=1",
            f"./config.sh --url https://github.com/{opts['org']}/{opts['repo']} --token {opts['token']} --labels {label}",
            "./run.sh"
        ])
        
        try:
            response = self.client.run_instances(
                ImageId=opts['ami_id'],
                InstanceType=opts['instance_type'],
                MinCount=1,
                MaxCount=1,
                UserData=user_data.encode('ascii'),
                SubnetId=opts['subnet_id'],
                SecurityGroupIds=[opts['security_group_id']],
                IamInstanceProfile={ "Name": opts['role_name'] },
                TagSpecifications=[{
                        'ResourceType': 'instance',
                        'Tags': [
                            {'Key': 'AppName', 'Value': 'ec2-self-hosted-runner'},
                            {'Key': 'Backup', 'Value': 'no'},
                            {'Key': 'Environment', 'Value': 'poc'},
                            {'Key': 'Name', 'Value': 'plt-self-hosted-gh-runner-ec2'},
                            {'Key': 'Product', 'Value': 'plt'},
                            {'Key': 'GithubRunnerLabel', 'Value': label},
                            {'Key': 'DataClassification', 'Value': 'internal'},
                            {'Key': 'BusinessUnit', 'Value': 'travel.poc'},
                            {'Key': 'InfraOwner', 'Value': 'manasjit.mohanty@tavisca.com'}
                        ]
                    }
                ]
            )
        except botocore.exceptions.ClientError as error:
            print('AWS EC2 instance starting error');
            print(error)
            sys.exit(1)
            # return {
            #     "statusCode": 400,
            #     "body": str(error)
            # }
        else:
            instance_id = response['Instances'][0]['InstanceId']
            print(f"AWS EC2 instance {instance_id} is started")
            waiter = self.client.get_waiter('instance_running')
            waiter.wait(InstanceIds=[instance_id])
            print(f"Instance {instance_id} is running")

            return {
                "statusCode": 200,
                "body": json.dumps({
                    "InstanceId": instance_id,
                    "Label": label
                })
            }
                
    def terminate_instance(self, instance_id):
        try:
            self.client.terminate_instances(InstanceIds=[instance_id])
        except botocore.exceptions.ClientError as error:
            print(error)
            sys.exit(1)
            # return {
            #     "statusCode": 400,
            #     "body": str(error)
            # }
        else:
            msg = f"Instance {instance_id} is terminated successfully"
            print(msg)
            return {
                "statusCode": 200,
                "body": msg
            }
