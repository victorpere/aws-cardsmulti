import json
import boto3
import os

dynamodb = boto3.client('dynamodb')


def handle(event, context):
    # Setup
    apigatewaymanagementapi = boto3.client('apigatewaymanagementapi', 
    endpoint_url = "https://" + event["requestContext"]["domainName"] + "/" + event["requestContext"]["stage"])

    # Request content
    senderConnectionId = event['requestContext']['connectionId']
    body = json.loads(event['body'])
    message = body['message']
    recepients = body['recepients']
    connectionIds = recepients.split(",")

    sendData = json.dumps({
        "status": "Message",
        "sender": senderConnectionId,
        "message": message,
        "recepients": recepients
    }).encode('utf-8')

    # Emit the recieved message to all the connected devices
    for connectionId in connectionIds:
        if connectionId and connectionId != senderConnectionId:
            apigatewaymanagementapi.post_to_connection(
                Data=sendData,
                ConnectionId=connectionId
            )

    return {}