import json
import boto3
import os
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource('dynamodb')
dbclient = boto3.client('dynamodb')

def handle(event, context):
    # Setup
    gamesTable = dynamodb.Table(os.environ['GAMES_TABLE_NAME'])
    apigatewaymanagementapi = boto3.client('apigatewaymanagementapi', 
    endpoint_url = "https://" + event["requestContext"]["domainName"] + "/" + event["requestContext"]["stage"])

    # Request content
    connectionId = event['requestContext']['connectionId']
    requestBody = json.loads(event['body'])
    gameId = requestBody['gameId']

    # Retrieve the game
    games = gamesTable.query(
        KeyConditionExpression=Key('gameId').eq(gameId)
    )

    # Create list of gameIds
    gameIds = []
    for game in games['Items']:
        gameIds.append({ 'gameId': game['gameId'], 'creator': game['creator'] })

    # Send back list of gameIds:
    apigatewaymanagementapi.post_to_connection(
            Data=json.dumps({
                'status': 'GamesList', 
                'gameIds': gameIds
            }),
            ConnectionId=connectionId
        )

    return {}