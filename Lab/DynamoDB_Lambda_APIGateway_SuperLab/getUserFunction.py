import json
import boto3
import os

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
table = dynamodb.Table(os.getenv('TABLE_NAME', 'UsersTable'))

def lambda_handler(event, context):
    # Read userId from path parameter
    path_params = event.get('pathParameters') or {}
    user_id = path_params.get('id')  # /users/{id} -> 'id'

    if not user_id:
        return {"statusCode": 400, "body": json.dumps({"error": "userId required"})}

    response = table.get_item(Key={"userId": user_id})
    item = response.get('Item')

    if not item:
        return {"statusCode": 404, "body": json.dumps({"error": "User not found"})}

    return {"statusCode": 200, "body": json.dumps(item)}
