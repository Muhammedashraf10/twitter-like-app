import json
import boto3
import hashlib
import jwt
import time

dynamodb = boto3.resource('dynamodb')
users_table = dynamodb.Table('Users')

SECRET_KEY = "Add Yours"

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
        'Cache-Control': 'no-store'  # Prevents caching of sensitive data
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

    # Retrieve user from DynamoDB
    response = users_table.get_item(Key={'username': username})
    print("DynamoDB Response:", response)  # Debugging

    if 'Item' not in response:
        return {
            'statusCode': 401,
            'body': json.dumps('User not found'),
            'headers': headers
        }

    stored_hash = response['Item']['password_hash']
    entered_hash = hash_password(password)

    print(f"Stored Hash: {stored_hash}")  # Debugging
    print(f"Entered Hash: {entered_hash}")  # Debugging

    if stored_hash != entered_hash:
        return {
            'statusCode': 401,
            'body': json.dumps('Invalid credentials'),
            'headers': headers
        }

    # Generate JWT token
    token = jwt.encode({
        'username': username,
        'exp': int(time.time()) + 3600  # 1-hour expiry
    }, SECRET_KEY, algorithm='HS256')

    return {
        'statusCode': 200,
        'body': json.dumps({'token': token}),
        'headers': headers
    }
