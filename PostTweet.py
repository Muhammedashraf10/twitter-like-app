import json
import boto3
import uuid
import time
import jwt

dynamodb = boto3.resource('dynamodb')
tweets_table = dynamodb.Table('Tweets')
users_table = dynamodb.Table('Users')

SECRET_KEY = "Add Yours"

def verify_token(event):
    """Verifies the JWT token from request headers."""
    auth_header = event.get('headers', {}).get('Authorization', '')
    if not auth_header.startswith("Bearer "):
        return None
    token = auth_header.split(" ")[1]
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None

def check_user_exists(username):
    """Checks if the user exists in the Users table."""
    response = users_table.get_item(Key={'username': username})
    return 'Item' in response

def lambda_handler(event, context):
    # Define headers with CORS, X-Content-Type-Options, and Cache-Control
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
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

    # Verify user authentication
    decoded_token = verify_token(event)
    if not decoded_token:
        return {
            'statusCode': 401,
            'body': json.dumps('Unauthorized: Invalid or expired token'),
            'headers': headers
        }

    # Extract username from token
    username = decoded_token.get('username')

    # Ensure the user exists in the Users table
    if not check_user_exists(username):
        return {
            'statusCode': 403,
            'body': json.dumps('Forbidden: User does not exist'),
            'headers': headers
        }

    # Parse request body
    try:
        body = json.loads(event.get('body', '{}'))
    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'body': json.dumps('Invalid JSON format'),
            'headers': headers
        }

    content = body.get('content')
    if not content:
        return {
            'statusCode': 400,
            'body': json.dumps('Tweet content is required'),
            'headers': headers
        }

    # Generate unique tweet ID and timestamp
    tweet_id = str(uuid.uuid4())
    timestamp = int(time.time())

    try:
        # Save the tweet in DynamoDB
        tweets_table.put_item(Item={
            'tweet_id': tweet_id,
            'username': username,
            'content': content,
            'timestamp': timestamp
        })
        return {
            'statusCode': 201,
            'body': json.dumps({'message': 'Tweet posted successfully', 'tweet_id': tweet_id}),
            'headers': headers
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f'Internal Server Error: {str(e)}'),
            'headers': headers
        }
