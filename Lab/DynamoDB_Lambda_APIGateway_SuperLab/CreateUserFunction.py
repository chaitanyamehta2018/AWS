import json, boto3, os
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.getenv('TABLE_NAME', 'UsersTable'))

def lambda_handler(event, context):
    body = json.loads(event.get('body', '{}'))
    user_id, name, email = body.get('userId'), body.get('name'), body.get('email')

    if not (user_id and name and email):
        return {"statusCode":400,"body":json.dumps({"error":"userId, name, email required"})}

    item = {"userId": user_id, "name": name, "email": email}
    table.put_item(Item=item)
    return {"statusCode":200,"body":json.dumps({"message":"User created","user":item})}
