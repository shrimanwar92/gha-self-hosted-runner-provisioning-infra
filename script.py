import requests
import sys
import os
import json
import argparse

def start_instance():
    try:
        response = requests.post(
            "https://tce5rsec11.execute-api.us-east-1.amazonaws.com/v1/invoke",
            json={
                "org": "org-nilay-shrimanwar",
                "mode": "start",
                "account_number": "535190322927",
                "subnet_id": "subnet-09d111c2cd2384b89",
                "security_group_id": "sg-055d78f333bc7ec3a"
            }            
        ).json()
        print(response)
    except BaseException as error:
        print(error)
        sys.exit(1)
    else:
        #response = json.loads(response['body'])
        # with open(os.environ['GITHUB_OUTPUT'], 'a') as fh:
        #     print(f"instance_id={response['InstanceId']}", file=fh)
        #     print(f"label={response['Label']}", file=fh)

        return response
    
def stop_instance():
    try:
        response = requests.post(
            "https://tce5rsec11.execute-api.us-east-1.amazonaws.com/v1/invoke",
            json={
                "org": "org-nilay-shrimanwar",
                "mode": "stop",
                "account_number": "535190322927",
                "instance_id": "i-0e8e796806befab3f",
                "runner_label": "ps5d41h"
            },
            headers={
                "Content-Type": "application/json"
            }          
        ).json()
    except BaseException as error:
        print(error)
        sys.exit(1)
    else:
        return response
    
parser = argparse.ArgumentParser()
parser.add_argument("-m", "--mode", required=True, help="lambda mode to run")
args = vars(parser.parse_args())

if args["mode"] == "start":
    start_instance()
elif args["mode"] == "stop":
    stop_instance()
else:
    print("Please provide a valid mode: start or stop")
    sys.exit(1)