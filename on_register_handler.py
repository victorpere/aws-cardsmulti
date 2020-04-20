import json
import boto3
import os

dynamodb = boto3.client('dynamodb')


def handle(event, context):
    connectionId = event['requestContext']['connectionId']
    sender = json.loads(event['body'])['sender']

    # Update the connectionName to the sender name
    tableName = os.environ['SOCKET_CONNECTIONS_TABLE_NAME']

    response = dynamodb.update_item(
        TableName=tableName,
        Key={ 'connectionId': {'S': connectionId}},
        UpdateExpression="set connectionName = :s",
        ExpressionAttributeValues={
            ':s': { 'S': sender }
        },
        ReturnValues="UPDATED_NEW"
    )

    return {}