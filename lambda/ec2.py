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
    label: str


class EC2Utils():
    def __init__(self) -> None:
        self.client = boto3.client('ec2')
        
    def start_instance(self, **opts: InstanceOptions):
        print(f"Runner label: {opts['label']}")
        
        user_data = "\n".join([
            "#!/bin/bash",
            "mkdir -p actions-runner && cd actions-runner",
            "case $(uname -m) in aarch64) ARCH='arm64' ;; amd64|x86_64) ARCH='x64' ;; esac && export RUNNER_ARCH=${ARCH}",
            "curl -O -L https://github.com/actions/runner/releases/download/v2.299.1/actions-runner-linux-${RUNNER_ARCH}-2.299.1.tar.gz",
            "tar xzf ./actions-runner-linux-${RUNNER_ARCH}-2.299.1.tar.gz",
            "export RUNNER_ALLOW_RUNASROOT=1",
            f"./config.sh --url https://github.com/{opts['org']}/{opts['repo']} --token {opts['token']} --labels {opts['label']}",
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
                            {'Key': 'GithubRunnerLabel', 'Value': opts['label']},
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
                    "Label": opts['label']
                })
            }
                
    def terminate_instance(self, instance_id):
        try:
            self.client.terminate_instances(InstanceIds=[instance_id])
        except botocore.exceptions.ClientError as error:
            print(error)
            sys.exit(1)
        else:
            msg = f"Instance {instance_id} is terminated successfully"
            print(msg)
            return {
                "statusCode": 200,
                "body": msg
            }
