import json
import boto3
import os

# Receive data from a connection and send it to all the other connections in the game
def handle(event, context):
    # Setup
    apigatewaymanagementapi = boto3.client('apigatewaymanagementapi', 
    endpoint_url = "https://" + event["requestContext"]["domainName"] + "/" + event["requestContext"]["stage"])

    # Request content
    requestBody = json.loads(event['body'])
    connectionIds = requestBody['connections']
    data = requestBody['data']

    # Send data
    for connectionId in connectionIds:
        apigatewaymanagementapi.post_to_connection(
            Data=data,
            ConnectionId=connectionId
        )

    return {}