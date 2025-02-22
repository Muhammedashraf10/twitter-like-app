import json
import boto3
from decimal import Decimal
import jwt

dynamodb = boto3.resource('dynamodb')
tweets_table = dynamodb.Table('Tweets')
users_table = dynamodb.Table('Users')

SECRET_KEY = "Add Yours"

def verify_token(event):
    auth_header = event.get('headers', {}).get('Authorization', '')
    if not auth_header.startswith("Bearer "):
        return None
    token = auth_header.split(" ")[1]
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return decoded_token
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None

def check_user_exists(username):
    response = users_table.get_item(Key={'username': username})
    return 'Item' in response

def decimal_to_int(obj):
    if isinstance(obj, list):
        return [decimal_to_int(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: decimal_to_int(v) for k, v in obj.items()}
    elif isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)
    else:
        return obj

def lambda_handler(event, context):
    cors_headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Authorization',
        'Access-Control-Allow-Methods': 'GET, OPTIONS'
    }

    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': cors_headers,
            'body': json.dumps('CORS preflight response')
        }

    decoded_token = verify_token(event)
    if not decoded_token:
        return {
            'statusCode': 401,
            'body': json.dumps('Unauthorized: Invalid or expired token'),
            'headers': cors_headers
        }

    username = decoded_token.get('username')
    if not check_user_exists(username):
        return {
            'statusCode': 403,
            'body': json.dumps('Forbidden: User does not exist'),
            'headers': cors_headers
        }

    try:
        response = tweets_table.scan()
        tweets = response.get('Items', [])
        tweets = decimal_to_int(tweets)
        tweets.sort(key=lambda x: x['timestamp'], reverse=True)
        return {
            'statusCode': 200,
            'body': json.dumps(tweets),
            'headers': cors_headers
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f'Internal Server Error: {str(e)}'),
            'headers': cors_headers
        }
