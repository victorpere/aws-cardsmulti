import json
import boto3
import os

# Receive data from a connection and send it to all the other connections in the game
def handle(event, context):
    # Setup
    apigatewaymanagementapi = boto3.client('apigatewaymanagementapi', 
    endpoint_url = "https://" + event["requestContext"]["domainName"] + "/" + event["requestContext"]["stage"])

    # Request content
    senderConnectionId = event['requestContext']['connectionId']
    body = json.loads(event['body'])
    data = body['data']
    recepients = body['recepients']
    status = body['type']
    connectionIds = recepients.split(",")

    # Emit the recieved data to all the connected devices
    for connectionId in connectionIds:
        apigatewaymanagementapi.post_to_connection(
            Data=json.dumps({ 
                "status": status,
                "sender": senderConnectionId,
                "data": data,
                "recepients": recepients
            }),
            ConnectionId=connectionId
        )

    return {}