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