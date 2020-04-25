import json
import boto3
import os
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.client('dynamodb')


def handle(event, context):
    connectionId = event['requestContext']['connectionId']
    requestBody = json.loads(event['body'])
    playerName = requestBody['playerName']
    gameCode = requestBody['gameCode']

    # Find matching game
    gamesTable = dynamodb.Table(os.environ['GAMES_TABLE_NAME'])
    games = gamesTable.query(
        KeyConditionExpression=Key('gameCode').eq(gameCode)
    )

    

    # Update gameId

    # Send connectionIds to all players in the game

    return {}