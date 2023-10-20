import boto3
import cfnresponse
import time
import json
import requests
import os
from os import environ

accept = "application/json"
content_type = "application/json"
runtime_region = os.environ['AWS_REGION']
stepfunctions = boto3.client("stepfunctions")

def lambda_handler (event, context):

    print (event)
    aws_account_id = context.invoked_function_arn.split(":")[4]
    
    if event['ResourceProperties']["dryRun"] == "true":
        event['ResourceProperties']["dryRun"] = True
    elif event['ResourceProperties']["dryRun"] == "false":
        event['ResourceProperties']["dryRun"] = False
        
    if event['ResourceProperties']["supportOSSClusterApi"] == "true":
        event['ResourceProperties']["supportOSSClusterApi"] = True
    elif event['ResourceProperties']["supportOSSClusterApi"] == "false":
        event['ResourceProperties']["supportOSSClusterApi"] = False
    
    if event['ResourceProperties']["useExternalEndpointForOSSClusterApi"] == "true":
        event['ResourceProperties']["useExternalEndpointForOSSClusterApi"] = True
    elif event['ResourceProperties']["useExternalEndpointForOSSClusterApi"] == "false":
        event['ResourceProperties']["useExternalEndpointForOSSClusterApi"] = False
        
    if event['ResourceProperties']["replication"] == "true":
        event['ResourceProperties']["replication"] = True
    elif event['ResourceProperties']["replication"] == "false":
        event['ResourceProperties']["replication"] = False
    
    if "active" in event['ResourceProperties']:   
        if event['ResourceProperties']["active"] == "true":
            event['ResourceProperties']["active"] = True
        elif event['ResourceProperties']["active"] == "false":
            event['ResourceProperties']["active"] = False
            
    if "enableTls" in event['ResourceProperties']:    
        if event['ResourceProperties']["enableTls"] == "true":
            event['ResourceProperties']["enableTls"] = True
        elif event['ResourceProperties']["enableTls"] == "false":
            event['ResourceProperties']["enableTls"] = False
        
    throughputMeasurement = {}
    if "by" in event['ResourceProperties']:
        throughputMeasurement["by"] = event['ResourceProperties']["by"]
    if "value" in event['ResourceProperties']:
        throughputMeasurement["value"] = int(event['ResourceProperties']["value"])
        
    remoteBackup = {}
    if "active" in event['ResourceProperties']:
        remoteBackup["active"] = event['ResourceProperties']["active"]
    if "interval" in event['ResourceProperties']:
        remoteBackup["interval"] = event['ResourceProperties']["interval"]
    if "timeUTC" in event['ResourceProperties']:
        remoteBackup["timeUTC"] = event['ResourceProperties']["timeUTC"]
    if "storageType" in event['ResourceProperties']:
        remoteBackup["storageType"] = event['ResourceProperties']["storageType"]
    if "storagePath" in event['ResourceProperties']:
        remoteBackup["storagePath"] = event['ResourceProperties']["storagePath"]
        
    alertsList = []
    alertsDict = {}
    if "alertName" in event['ResourceProperties']:
        alertsDict["name"] = event['ResourceProperties']["alertName"]
    if "alertValue" in event['ResourceProperties']:
        alertsDict["value"] = event['ResourceProperties']["alertValue"]
    alertsList.append(alertsDict)
    
    modulesList = []
    modulesDict = {}
    if "moduleName" in event['ResourceProperties']:
        modulesDict["name"] = event['ResourceProperties']["moduleName"]
    if "parameters" in event['ResourceProperties']: 
        modulesDict["parameters"] = event['ResourceProperties']["parameters"]
    modulesList.append(modulesDict)
    
    callEvent = {}
    if "dryRun" in event['ResourceProperties']:
        callEvent["dryRun"] = event['ResourceProperties']["dryRun"]
    if "dbname" in event['ResourceProperties']:
        callEvent["name"] = event['ResourceProperties']["dbname"]
    if "protocol" in event['ResourceProperties']:
        callEvent["protocol"] = event['ResourceProperties']["protocol"]
    if "port" in event['ResourceProperties']:
        callEvent["port"] = event['ResourceProperties']["port"]
    if "memoryLimitInGb" in event['ResourceProperties']:
        callEvent["memoryLimitInGb"] = int(event['ResourceProperties']["memoryLimitInGb"])
    if "respVersion" in event['ResourceProperties']:
        callEvent["respVersion"] = event['ResourceProperties']["respVersion"]
    if "supportOSSClusterApi" in event['ResourceProperties']:
        callEvent["supportOSSClusterApi"] = event['ResourceProperties']["supportOSSClusterApi"]
    if "useExternalEndpointForOSSClusterApi" in event['ResourceProperties']:
        callEvent["useExternalEndpointForOSSClusterApi"] = event['ResourceProperties']["useExternalEndpointForOSSClusterApi"]
    if "dataPersistence" in event['ResourceProperties']:
        callEvent["dataPersistence"] = event['ResourceProperties']["dataPersistence"]
    if "dataEvictionPolicy" in event['ResourceProperties']:
        callEvent["dataEvictionPolicy"] = event['ResourceProperties']["dataEvictionPolicy"]
    if "replication" in event['ResourceProperties']:
        callEvent["replication"] = event['ResourceProperties']["replication"]
    if "replicaOf" in event['ResourceProperties']:
        callEvent["replicaOf"] = event['ResourceProperties']["replicaOf"]
    if "by" in event['ResourceProperties']:
        callEvent["throughputMeasurement"] = throughputMeasurement
    if "averageItemSizeInBytes" in event['ResourceProperties']:
        callEvent["averageItemSizeInBytes"] = int(event['ResourceProperties']["averageItemSizeInBytes"])
    if "active" in event['ResourceProperties']:
        callEvent["remoteBackup"] = remoteBackup
    if "sourceIp" in event['ResourceProperties']:
        callEvent["sourceIp"] = event['ResourceProperties']["sourceIp"]
    if "clientSslCertificate" in event['ResourceProperties']:
        callEvent["clientSslCertificate"] = event['ResourceProperties']["clientSslCertificate"]
    if "enableTls" in event['ResourceProperties']:
        callEvent["enableTls"] = event['ResourceProperties']["enableTls"]
    if "password" in event['ResourceProperties']:
        callEvent["password"] = event['ResourceProperties']["password"]
    if "saslUsername" in event['ResourceProperties']:
        callEvent["saslUsername"] = event['ResourceProperties']["saslUsername"]
    if "saslPassword" in event['ResourceProperties']:
        callEvent["saslPassword"] = event['ResourceProperties']["saslPassword"]
    if "alertName" in event['ResourceProperties']:
        callEvent["alerts"] = alertsList
    if "moduleName" in event['ResourceProperties']:
        callEvent["modules"] = modulesList
        
    print ("callEvent that is used as the actual API Call is bellow:")
    print (callEvent)
    
    subscription_id = event['ResourceProperties']["subscriptionId"]
    print ("Subscription ID is: " + str(subscription_id))
    
    global stack_name
    global base_url
    global x_api_key
    global x_api_secret_key 
    base_url = event['ResourceProperties']['baseURL']
    x_api_key =  RetrieveSecret("redis/x_api_key")["x_api_key"]
    x_api_secret_key =  RetrieveSecret("redis/x_api_secret_key")["x_api_secret_key"]
    stack_name = str(event['StackId'].split("/")[1])
    responseData = {}
    
    responseStatus = 'SUCCESS'
    responseURL = event['ResponseURL']
    responseBody = {'Status': responseStatus,
                    'PhysicalResourceId': context.log_stream_name,
                    'StackId': event['StackId'],
                    'RequestId': event['RequestId'],
                    'LogicalResourceId': event['LogicalResourceId']
                    }
                    
    if event['RequestType'] == "Create":
        responseValue = PostDatabase(callEvent, subscription_id)
        print (responseValue)

        try:
            db_id, db_description = GetDatabaseId (responseValue['links'][0]['href'])
            print ("Description for Database with id " + str(db_id) + " is: " + str(db_description))
            responseData.update({"SubscriptionId":str(subscription_id), "DatabaseId":str(db_id), "DatabaseDescription":str(db_description), "PostCall":str(callEvent)})
            responseBody.update({"Data":responseData})
            SFinput = {}
            SFinput["responseBody"] = responseBody
            SFinput["responseURL"] = responseURL
            SFinput["base_url"] = event['ResourceProperties']['baseURL']
            response = stepfunctions.start_execution(
                stateMachineArn = f'arn:aws:states:{runtime_region}:{aws_account_id}:stateMachine:FlexibleDatabase-StateMachine-{runtime_region}-{stack_name}',
                name = f'FlexibleDatabase-StateMachine-{runtime_region}-{stack_name}',
                input = json.dumps(SFinput)
                )
            print ("Output sent to Step Functions is the following:")
            print (json.dumps(SFinput))
        
        except:
            db_error = GetDatabaseError (responseValue['links'][0]['href'])
            responseStatus = 'FAILED'
            reason = str(db_error)
            if responseStatus == 'FAILED':
                responseBody.update({"Status":responseStatus})
                if "Reason" in str(responseBody):
                    responseBody.update({"Reason":reason})
                else:
                    responseBody["Reason"] = reason
                GetResponse(responseURL, responseBody)
    
    if event['RequestType'] == "Update":
        cf_sub_id, cf_event, cf_db_id, cf_db_description = CurrentOutputs()
        PhysicalResourceId = event['PhysicalResourceId']
        responseBody.update({"PhysicalResourceId":PhysicalResourceId})
        
        if event['ResourceProperties']["enableDefaultUser"] == "true":
            event['ResourceProperties']["enableDefaultUser"] = True
        elif event['ResourceProperties']["enableDefaultUser"] == "false":
            event['ResourceProperties']["enableDefaultUser"] = False
        if "regexRules" in event['ResourceProperties']:
            callEvent["regexRules"] = event['ResourceProperties']["regexRules"]
        if "enableDefaultUser" in event['ResourceProperties']:
            callEvent["enableDefaultUser"] = event['ResourceProperties']["enableDefaultUser"]
        db_status = GetDatabaseStatus(cf_db_id)

        if str(db_status) == "active":
            responseValue = PutDatabase(cf_sub_id, cf_db_id, callEvent)
            cf_event = cf_event.replace("\'", "\"")
            cf_event = cf_event.replace("False", "false")
            cf_event = cf_event.replace("True", "true")
            cf_event = json.loads(cf_event)
            cf_event.update(callEvent)
            
            print ("This is the event key after PUT call:")
            print (cf_event)
            
            responseData.update({"SubscriptionId":str(subscription_id), "DatabaseId":str(db_id), "DatabaseDescription":str(db_description), "PostCall":str(callEvent)})
            print (responseData)
            responseBody.update({"Data":responseData})
            
            GetResponse(responseURL, responseBody)
        
        elif str(db_status) == "pending":
            responseValue = PutDatabase(cf_sub_id, cf_db_id, callEvent)
            print ("this is response value for update in pending")
            print (responseValue)
            db_error = GetDatabaseError (responseValue['links'][0]['href'])
            responseStatus = 'FAILED'
            reason = str(db_error)
            if responseStatus == 'FAILED':
                responseBody.update({"Status":responseStatus})
                if "Reason" in str(responseBody):
                    responseBody.update({"Reason":reason})
                else:
                    responseBody["Reason"] = reason
                GetResponse(responseURL, responseBody)
                
        elif str(db_status) == "deleting":
            responseValue = PutDatabase(cf_sub_id, cf_db_id, callEvent)
            db_error = GetDatabaseError (responseValue['links'][0]['href'])
            responseStatus = 'FAILED'
            reason = str(db_error)
            if responseStatus == 'FAILED':
                responseBody.update({"Status":responseStatus})
                if "Reason" in str(responseBody):
                    responseBody.update({"Reason":reason})
                else:
                    responseBody["Reason"] = reason
                GetResponse(responseURL, responseBody)
            
    if event['RequestType'] == "Delete":
        try:
            cf_sub_id, cf_event, cf_db_id, cf_db_description = CurrentOutputs()
        except:
            responseStatus = 'SUCCESS'
            responseBody.update({"Status":responseStatus})
            GetResponse(responseURL, responseBody)
        databases = GetAllDatabases(cf_sub_id)
        if str(cf_db_id) in str(databases):
            #try:
            responseValue = DeleteDatabase(cf_sub_id, cf_db_id)
            responseData.update({"SubscriptionId":str(subscription_id), "DatabaseId":str(db_id), "DatabaseDescription":str(db_description), "PostCall":str(callEvent)})
            print (responseData)
            responseBody.update({"Data":responseData})
            GetResponse(responseURL, responseBody)
            # except:
            #     responseStatus = 'FAILED'
            #     reason = "Unable to delete database"
            #     if responseStatus == 'FAILED':
            #         responseBody.update({"Status":responseStatus})
            #         if "Reason" in str(responseBody):
            #             responseBody.update({"Reason":reason})
            #         else:
            #             responseBody["Reason"] = reason
            #         GetResponse(responseURL, responseBody)
        else:
            print("Database does not exists")
            GetResponse(responseURL, responseBody)

def RetrieveSecret(secret_name):
    headers = {"X-Aws-Parameters-Secrets-Token": os.environ.get('AWS_SESSION_TOKEN')}

    secrets_extension_endpoint = "http://localhost:2773/secretsmanager/get?secretId=" + str(secret_name)
    r = requests.get(secrets_extension_endpoint, headers=headers)
    secret = json.loads(r.text)["SecretString"]
    secret = json.loads(secret)

    return secret

def CurrentOutputs():
    cloudformation = boto3.client('cloudformation')
    cf_response = cloudformation.describe_stacks(StackName=stack_name)
    for output in cf_response["Stacks"][0]["Outputs"]:
        if "SubscriptionId" in str(output): 
            cf_sub_id = output["OutputValue"]

        if "PostCall" in str(output): 
            cf_event = output["OutputValue"]

        if "DatabaseId" in str(output): 
            cf_db_id = output["OutputValue"]

        if "DatabaseDescription" in str(output): 
            cf_db_description = output["OutputValue"]
            
    print ("cf_sub_id is: " + str(cf_sub_id))
    print ("cf_event is: " + str(cf_event))
    print ("cf_db_id is: " + str(cf_db_id))
    print ("cf_db_description is: " + str(cf_db_description))
    return cf_sub_id, cf_event, cf_db_id, cf_db_description
    
def PostDatabase (event, subscription_id):
    url = base_url + "/v1/subscriptions/" + str(subscription_id) + "/databases"
    
    response = requests.post(url, headers={"accept":accept, "x-api-key":x_api_key, "x-api-secret-key":x_api_secret_key, "Content-Type":content_type}, json = event)
    response_json = response.json()
    return response_json
    Logs(response_json)
    
def GetDatabase (subscription_id, database_id):
    url = base_url + "/v1/subscriptions/" + str(subscription_id) + "/databases/" + str(database_id)
    count = 0
    response = requests.get(url, headers={"accept":accept, "x-api-key":x_api_key, "x-api-secret-key":x_api_secret_key})
    response = response.json()
    
    while "databaseId" not in str(response) and count < 120:
        time.sleep(1)
        count += 1
        print (str(response))
        response = requests.get(response['links'][0]['href'], headers={"accept":accept, "x-api-key":x_api_key, "x-api-secret-key":x_api_secret_key})
        response = response.json()
        
    print (response)
    return response
    Logs(response)
    
def GetDatabaseStatus (subscription_id, database_id):
    url = base_url + "/v1/subscriptions/" + str(subscription_id) + "/databases/" + str(database_id)
    
    response = requests.get(url, headers={"accept":accept, "x-api-key":x_api_key, "x-api-secret-key":x_api_secret_key})
    response = response.json()
    db_status = response["status"]
    print ("Database status is: " + db_status)
    return db_status
    
def GetDatabaseId (url):
    response = requests.get(url, headers={"accept":accept, "x-api-key":x_api_key, "x-api-secret-key":x_api_secret_key})
    response = response.json()
    print (str(response))
    count = 0
    
    while "resourceId" not in str(response) and count < 120:
        time.sleep(1)
        count += 1
        print (str(response))
        response = requests.get(url, headers={"accept":accept, "x-api-key":x_api_key, "x-api-secret-key":x_api_secret_key})
        response = response.json()

    db_id = response["response"]["resourceId"]
    db_description = response["description"]
    return db_id, db_description
    
def GetAllDatabases (subscription_id, offset = 0, limit = 100):
    url = base_url + "/v1/subscriptions/" + str(subscription_id) + "/databases?offset=" + str(offset) + "&limit=" + str(limit)
    
    response = requests.get(url, headers={"accept":accept, "x-api-key":x_api_key, "x-api-secret-key":x_api_secret_key})
    response_json = response.json()
    return response_json
    Logs(response_json)
    
def GetDatabaseError (url):
    response = requests.get(url, headers={"accept":accept, "x-api-key":x_api_key, "x-api-secret-key":x_api_secret_key})
    response = response.json()
    count = 0

    while "processing-error" not in str(response) and count < 120:
        time.sleep(1)
        count += 1
        response = requests.get(url, headers={"accept":accept, "x-api-key":x_api_key, "x-api-secret-key":x_api_secret_key})
        response = response.json()

    db_error_description = response["response"]["error"]["description"]
    return db_error_description
    
def PutDatabase (subscription_id, database_id, event):
    url = base_url + "/v1/subscriptions/" + str(subscription_id) + "/databases/" + str(database_id)
    print (event)
    
    throughputMeasurement = {}
    for key in list(event[throughputMeasurement]):
    	if key == "by":
    	    throughputMeasurement['by'] = event[key]
    	if key == "value":
    	    throughputMeasurement['value'] = event[key]
    
    remoteBackup = {}
    for key in list(event[remoteBackup]):
    	if key == "active":
    	    remoteBackup['active'] = event[key]
    	if key == "interval":
    	    remoteBackup['interval'] = event[key]
    	if key == "timeUTC":
    	    remoteBackup['timeUTC'] = event[key]
    	if key == "storageType":
    	    remoteBackup['storageType'] = event[key]
    	if key == "storagePath":
    	    remoteBackup['storagePath'] = event[key]
    
    alertsList = []
    alertsDict = {}
    for key in list(event[alerts]):
    	if key == "alertName":
    	    alertsDict['name'] = event[key]
    	if key == "alertValue":
    	    alertsDict['value'] = event[key]
    alertsList.append(alertsDict)
    
    update_dict = {}
    for key in list(event):
    	if key == "dryRun":
    	    update_dict['dryRun'] = event[key]
    	if key == "name":
    	    update_dict['name'] = event[key]
    	if key == "memoryLimitInGb":
    	    update_dict['memoryLimitInGb'] = event[key]
    	if key == "respVersion":
    	    update_dict['respVersion'] = event[key]
    	if key == "throughputMeasurement":
    	    update_dict['throughputMeasurement'] = throughputMeasurement
    	if key == "dataPersistence":
    	    update_dict['dataPersistence'] = event[key]
    	if key == "dataEvictionPolicy":
    	    update_dict['dataEvictionPolicy'] = event[key]
    	if key == "replication":
    	    update_dict['replication'] = event[key]
    	if key == "regexRules":
    	    update_dict['regexRules'] = event[key]
    	if key == "replicaOf":
    	    update_dict['replicaOf'] = event[key]
    	if key == "supportOSSClusterApi":
    	    update_dict['supportOSSClusterApi'] = event[key]
    	if key == "useExternalEndpointForOSSClusterApi":
    	    update_dict['useExternalEndpointForOSSClusterApi'] = event[key]
    	if key == "password":
    	    update_dict['password'] = event[key]
    	if key == "saslUsername":
    	    update_dict['saslUsername'] = event[key]
    	if key == "saslPassword":
    	    update_dict['saslPassword'] = event[key]
    	if key == "sourceIp":
    	    update_dict['sourceIp'] = event[key]
    	if key == "clientSslCertificate":
    	    update_dict['clientSslCertificate'] = event[key]
    	if key == "enableTls":
    	    update_dict['enableTls'] = event[key]
    	if key == "enableDefaultUser":
    	    update_dict['enableDefaultUser'] = event[key]
    	if key == "remoteBackup":
    	    update_dict['remoteBackup'] = remoteBackup
    	if key == "alerts":
    	    update_dict['alerts'] = alertsList
    print ("Dict to PUT is:")
    print (update_dict)
    
    response = requests.put(url, headers={"accept":accept, "x-api-key":x_api_key, "x-api-secret-key":x_api_secret_key, "Content-Type":content_type}, json = update_dict)
    print ("PutSubscription response is:")
    print(response)
    response_json = response.json()
    return response_json
    Logs(response_json)
    
def DeleteDatabase (subscription_id, database_id):
    url = base_url + "/v1/subscriptions/" + str(subscription_id) + "/databases/" + str(database_id)
    
    response_peer = requests.delete(url, headers={"accept":accept, "x-api-key":x_api_key, "x-api-secret-key":x_api_secret_key})
    Logs(response_peer.json())

def GetResponse(responseURL, responseBody): 
    responseBody = json.dumps(responseBody)
    req = requests.put(responseURL, data = responseBody)
    print ('RESPONSE BODY:n' + responseBody)
    
def Logs(response_json):
    error_url = response_json['links'][0]['href']
    error_message = requests.get(error_url, headers={"accept":accept, "x-api-key":x_api_key, "x-api-secret-key":x_api_secret_key})
    error_message_json = error_message.json()
    if 'description' in error_message_json:
        while response_json['description'] == error_message_json['description']:
            error_message = requests.get(error_url, headers={"accept":accept, "x-api-key":x_api_key, "x-api-secret-key":x_api_secret_key})
            error_message_json = error_message.json()
        print(error_message_json)
    else:
        print ("No errors")
