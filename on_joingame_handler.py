import json
import boto3
import os
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource('dynamodb')


def handle(event, context):
    # Setup
    connectionsTable = dynamodb.Table(os.environ['SOCKET_CONNECTIONS_TABLE_NAME'])
    gamesTable = dynamodb.Table(os.environ['GAMES_TABLE_NAME'])
    apigatewaymanagementapi = boto3.client('apigatewaymanagementapi', 
    endpoint_url = "https://" + event["requestContext"]["domainName"] + "/" + event["requestContext"]["stage"])

    # Request content
    connectionId = event['requestContext']['connectionId']
    requestBody = json.loads(event['body'])
    playerName = requestBody['playerName']
    gameCode = requestBody['gameCode']

    # Retrieve the game
    games = gamesTable.query(
        IndexName='gameCodeIndex',
        KeyConditionExpression=Key('gameCode').eq(gameCode)
    )

    # No matching games
    if games['Count'] == 0:
        apigatewaymanagementapi.post_to_connection(
                Data=json.dumps({'status': 'Game not found', 'gameCode': gameCode}),
                ConnectionId=connectionId
            )
        return {}

    # Send connectionIds to all players in the game
    apigatewaymanagementapi.post_to_connection(
            Data=json.dumps({'status': 'Game found', 'gameCode': gameCode}),
            ConnectionId=connectionId
        )

    return {}