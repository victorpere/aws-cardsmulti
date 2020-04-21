import json
import boto3
import os
import uuid

dynamodb = boto3.client('dynamodb')


def handle(event, context):
    connectionId = event['requestContext']['connectionId']
    gameId = str(uuid.uuid4())

    # Create a new record for the game
    dynamodb.put_item(TableName=os.environ['GAMES_TABLE_NAME'], Item={'gameId': {'S': gameId}})
    
    # Send the gameId to the creator
    apigatewaymanagementapi = boto3.client('apigatewaymanagementapi', 
    endpoint_url = "https://" + event["requestContext"]["domainName"] + "/" + event["requestContext"]["stage"])

    apigatewaymanagementapi.post_to_connection(
            Data=json.dumps({'gameId': gameId}),
            ConnectionId=connectionId
        )

    return {}