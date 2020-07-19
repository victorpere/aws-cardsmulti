import json
import boto3
import os
import uuid
import random

dynamodb = boto3.client('dynamodb')
maxPlayersDefault = '4'

def handle(event, context):
    # Setup
    connectionsTableName = os.environ['SOCKET_CONNECTIONS_TABLE_NAME']
    gamesTableName = os.environ['GAMES_TABLE_NAME']
    apigatewaymanagementapi = boto3.client('apigatewaymanagementapi', 
    endpoint_url = "https://" + event["requestContext"]["domainName"] + "/" + event["requestContext"]["stage"])

    # Request content
    connectionId = event['requestContext']['connectionId']
    requestBody = json.loads(event['body'])
    playerName = requestBody['creator']
    maxPlayers = maxPlayersDefault
    gameId = str(uuid.uuid4())
    gameCode = str(random.randrange(1000,9999))

    # Create a new record for the game
    dynamodb.put_item(TableName=gamesTableName, Item={
        'gameId': {'S': gameId}, 
        'gameCode': {'S': gameCode}, 
        'creator': {'S': playerName},
        'players': {'SS': [ connectionId ]},
        'maxPlayers': {'N': maxPlayers }
    })
    
    # Update the connection record with the gameId and playerName
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
    apigatewaymanagementapi.post_to_connection(
            Data=json.dumps({
                'status': 'Created',
                'connectionId': connectionId,
                'playerName': playerName,
                'gameId': gameId,
                'creator': playerName,
                'connections': [ connectionId ],
                'gameCode': gameCode,
                'maxPlayers': maxPlayers
            }),
            ConnectionId=connectionId
        )

    return {}