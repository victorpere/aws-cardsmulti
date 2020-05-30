import json
import boto3
import os
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource('dynamodb')
dbclient = boto3.client('dynamodb')

def handle(event, context):
    # Setup
    connectionsTableName = os.environ['SOCKET_CONNECTIONS_TABLE_NAME']
    connectionsTable = dynamodb.Table(os.environ['SOCKET_CONNECTIONS_TABLE_NAME'])
    gamesTable = dynamodb.Table(os.environ['GAMES_TABLE_NAME'])
    apigatewaymanagementapi = boto3.client('apigatewaymanagementapi', 
    endpoint_url = "https://" + event["requestContext"]["domainName"] + "/" + event["requestContext"]["stage"])

    # Request content
    connectionId = event['requestContext']['connectionId']
    requestBody = json.loads(event['body'])
    playerName = requestBody['playerName']
    gameId = requestBody['gameId']

    # Retrieve the game
    games = gamesTable.query(
        KeyConditionExpression=Key('gameId').eq(gameId)
    )

    # No matching games
    if games['Count'] == 0:
        apigatewaymanagementapi.post_to_connection(
                Data=json.dumps({'status': 'Game not found', 'gameId': gameId}),
                ConnectionId=connectionId
            )
        return {}

    # Get game info
    game = games['Items'][0]
    gameId = game['gameId']
    creator = game['creator']
    players = str(game['players'])

    # Update the connection record with the gameId and playerName
    dbclient.update_item(
        TableName=connectionsTableName,
        Key={ 'connectionId': {'S': connectionId}},
        UpdateExpression="set gameId = :s, playerName = :p",
        ExpressionAttributeValues={
            ':s': { 'S': gameId },
            ':p': { 'S': playerName }
        },
        ReturnValues="UPDATED_NEW"
    )

    # Get all connection records in this game
    connections = connectionsTable.query(
        IndexName='gameIdIndex',
        KeyConditionExpression=Key('gameId').eq(gameId)
    )

    # Something is wrong
    if connections['Count'] == 0:
        apigatewaymanagementapi.post_to_connection(
                Data=json.dumps({ 'status': 'Error' }),
                ConnectionId=connectionId
            )
        return {}

    # Send confirmation
    apigatewaymanagementapi.post_to_connection(
            Data=json.dumps({
                'status': 'Joined', 
                'gameId': gameId,
                'creator': creator,
                'playerName': playerName
            }),
            ConnectionId=connectionId
        )

    # Create list of all connections
    connectionIds = []
    players = []
    for connectedConnection in connections['Items']:
        connectionIds.append(connectedConnection['connectionId'])
        players.append({
            'connectionId': connectedConnection['connectionId'],
            'playerName': connectedConnection['playerName']
        })

    # Send connectionIds to all players in the game
    for connectedConnection in connections['Items']:
            apigatewaymanagementapi.post_to_connection(
            Data=json.dumps({
                'status': 'New connection',
                'connectionId': connectionId,
                'playerName': playerName,
                'gameId': gameId,
                'creator': creator,
                'connections': connectionIds,
                'players' : players
            }),
            ConnectionId=connectedConnection['connectionId']
        )

    return {}