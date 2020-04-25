import json
import boto3
import os
import uuid
import random

dynamodb = boto3.client('dynamodb')


def handle(event, context):
    connectionId = event['requestContext']['connectionId']
    playerName = json.loads(event['body'])['creator']
    gameId = str(uuid.uuid4())
    gameCode = str(random.randrange(1000,9999))

    # Create a new record for the game
    dynamodb.put_item(TableName=os.environ['GAMES_TABLE_NAME'], Item={'gameId': {'S': gameId}, 'gameCode': {'S': gameCode}, 'creator': {'S': playerName}})
    
    # Update the connection record with the gameId and playerName
    connectionsTableName = os.environ['SOCKET_CONNECTIONS_TABLE_NAME']
    dynamodb.update_item(
        TableName=connectionsTableName,
        Key={ 'connectionId': {'S': connectionId}},
        UpdateExpression="set gameId = :s, playerName = :p",
        ExpressionAttributeValues={
            ':s': { 'S': gameId },
            ':p': { 'S': playerName }
        },
        ReturnValues="UPDATED_NEW"
    )

    # Send the gameId to the creator
    apigatewaymanagementapi = boto3.client('apigatewaymanagementapi', 
    endpoint_url = "https://" + event["requestContext"]["domainName"] + "/" + event["requestContext"]["stage"])

    apigatewaymanagementapi.post_to_connection(
            Data=json.dumps({'gameId': gameId, 'gameCode': gameCode}),
            ConnectionId=connectionId
        )

    return {}