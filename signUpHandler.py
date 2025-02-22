import json
import boto3
import hashlib
import time
import jwt  

dynamodb = boto3.resource('dynamodb')
users_table = dynamodb.Table('Users')

SECRET_KEY = "Add yours"

def hash_password(password):
    """Hashes password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def lambda_handler(event, context):
    # Define headers with CORS, X-Content-Type-Options, and Cache-Control
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'X-Content-Type-Options': 'nosniff',
        'Cache-Control': 'no-store'
    }

    # Handle preflight OPTIONS request
    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps('CORS preflight response')
        }

    try:
        body = json.loads(event.get('body', '{}'))
    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'body': json.dumps('Invalid JSON format'),
            'headers': headers
        }

    username = body.get('username')
    password = body.get('password')

    if not username or not password:
        return {
            'statusCode': 400,
            'body': json.dumps('Username and password are required'),
            'headers': headers
        }

    password_hash = hash_password(password)

    try:
        users_table.put_item(
            Item={
                'username': username,
                'password_hash': password_hash,
                'created_at': int(time.time())
            },
            ConditionExpression='attribute_not_exists(username)'  # Prevent duplicate users
        )
        # Generate JWT token
        token = jwt.encode({
            'username': username,
            'exp': int(time.time()) + 3600  # 1-hour expiry
        }, SECRET_KEY, algorithm='HS256')
        return {
            'statusCode': 201,
            'body': json.dumps({'token': token}),
            'headers': headers
        }
    
    except dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
        return {
            'statusCode': 409,
            'body': json.dumps('User already exists'),
            'headers': headers
        }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f'Internal Server Error: {str(e)}'),
            'headers': headers
        }
