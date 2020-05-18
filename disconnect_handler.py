import json
import boto3
import os
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource('dynamodb')
dbclient = boto3.client('dynamodb')

def handle(event, context):
    # Setup
    connectionsTable = dynamodb.Table(os.environ['SOCKET_CONNECTIONS_TABLE_NAME'])
    apigatewaymanagementapi = boto3.client('apigatewaymanagementapi', 
    endpoint_url = "https://" + event["requestContext"]["domainName"] + "/" + event["requestContext"]["stage"])

    # Request content
    connectionId = event['requestContext']['connectionId']

    # Retrieve connection
    thisConnection = connectionsTable.query(
        KeyConditionExpression=Key('connectionId').eq(connectionId)
    )

    if thisConnection['Count'] == 0:
        return {}

    # Delete connectionId from the database
    dbclient.delete_item(TableName=os.environ['SOCKET_CONNECTIONS_TABLE_NAME'], Key={'connectionId': {'S': connectionId}})

    gameId = thisConnection['Items'][0]['gameId']

    # Get all remaining connection records in this game
    connections = connectionsTable.query(
        IndexName='gameIdIndex',
        KeyConditionExpression=Key('gameId').eq(gameId)
    )

    # Create list of all connections
    connectionIds = []
    for connectedConnection in connections['Items']:
        connectionIds.append(connectedConnection['connectionId'])

    # Send connectionIds to all players in the game
    for connectedConnection in connections['Items']:
        apigatewaymanagementapi.post_to_connection(
            Data=json.dumps({
                'status': 'Connections update',
                'connectionId': connectionId,
                'playerName': '',
                'gameId': gameId,
                'connections': connectionIds
            }),
            ConnectionId=connectedConnection['connectionId']
        )

    return {}