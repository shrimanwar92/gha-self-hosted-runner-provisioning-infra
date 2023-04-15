import string
import random
import boto3
import json
import botocore
from typing import TypedDict

class InstanceOptions(TypedDict):
    org: str
    token: str
    instance_type: str
    subnet_id: str
    security_group_id: str
    role_name: str


class EC2Utils():
    def __init__(self, credentials) -> None:
        self.client = boto3.client(
            'ec2',
            aws_access_key_id=credentials['AccessKeyId'],
            aws_secret_access_key=credentials['SecretAccessKey'],
            aws_session_token=credentials['SessionToken']
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
        
        user_data = "\n".join([
            "#!/bin/bash",
            "mkdir actions-runner && cd actions-runner",
            "case $(uname -m) in aarch64) ARCH='arm64' ;; amd64|x86_64) ARCH='x64' ;; esac && export RUNNER_ARCH=${ARCH}",
            "curl -O -L https://github.com/actions/runner/releases/download/v2.303.0/actions-runner-linux-${RUNNER_ARCH}-2.303.0.tar.gz",
            "tar xzf ./actions-runner-linux-${RUNNER_ARCH}-2.303.0.tar.gz",
            "export RUNNER_ALLOW_RUNASROOT=1",
            f"./config.sh --url https://github.com/{opts['org']} --token {opts['token']} --labels {label}",
            "./run.sh"
        ])
        
        try:
            response = self.client.run_instances(
                ImageId="ami-0ee7455b4a7147df4",
                InstanceType=opts['instance_type'],
                MinCount=1,
                MaxCount=1,
                UserData=user_data.encode('ascii'),
                SubnetId=opts['subnet_id'],
                SecurityGroupIds=[opts['security_group_id']],
                IamInstanceProfile={ "Name": opts['role_name'] }    
            )
        except botocore.exceptions.ClientError as error:
            print('AWS EC2 instance starting error');
            print(error)
            return {
                "statusCode": 400,
                "body": str(error)
            }
        else:
            instance_id = response['Instances'][0]['InstanceId']
            print(f"AWS EC2 instance {instance_id} is started")
            self.add_tag(instance_id, label)
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
            return {
                "statusCode": 400,
                "body": str(error)
            }
        else:
            msg = f"Instance {instance_id} is terminated successfully"
            print(msg)
            return {
                "statusCode": 200,
                "body": msg
            }
        
    
    def add_tag(self, instance_id, label):
        self.client.create_tags(
            Resources=[
                instance_id,
            ],
            Tags=[
                {
                    'Key': 'Github-Runner-Label',
                    'Value': label
                },
            ]
        )