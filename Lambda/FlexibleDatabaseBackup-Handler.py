import boto3
import cfnresponse
import time
import json
import requests
import os
from os import environ

accept = "application/json"
content_type = "application/json"
# runtime_region = os.environ['AWS_REGION']
# stepfunctions = boto3.client("stepfunctions")

def lambda_handler (event, context):

    print (event)
    # aws_account_id = context.invoked_function_arn.split(":")[4]
    responseStatus = 'SUCCESS'
    responseURL = event['ResponseURL']
    responseBody = {'Status': responseStatus,
                    'PhysicalResourceId': context.log_stream_name,
                    'StackId': event['StackId'],
                    'RequestId': event['RequestId'],
                    'LogicalResourceId': event['LogicalResourceId']
                    }
    responseData.update({"SubscriptionId":str("1"), "DatabaseId":str("2"), "PostCall":str("3")})
    responseBody.update({"Data":responseData})
    GetResponse(responseURL, responseBody)
