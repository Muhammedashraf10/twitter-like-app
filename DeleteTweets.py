import json
import boto3
import jwt

# Initialize DynamoDB resources
dynamodb = boto3.resource('dynamodb')
tweets_table = dynamodb.Table('Tweets')
users_table = dynamodb.Table('Users')

# Secret key for JWT (must match other Lambdas)
SECRET_KEY = "Add yours"

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
        'Access-Control-Allow-Methods': 'DELETE, OPTIONS',
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

    # Get tweet_id from path parameters
    tweet_id = event.get('pathParameters', {}).get('tweet_id')
    if not tweet_id:
        return {
            'statusCode': 400,
            'body': json.dumps('Tweet ID is required'),
            'headers': headers
        }

    try:
        # Fetch tweet to verify ownership
        response = tweets_table.get_item(Key={'tweet_id': tweet_id})
        if 'Item' not in response or response['Item']['username'] != username:
            return {
                'statusCode': 403,
                'body': json.dumps('Forbidden: You can only delete your own tweets'),
                'headers': headers
            }

        # Delete the tweet
        tweets_table.delete_item(Key={'tweet_id': tweet_id})
        return {
            'statusCode': 200,
            'body': json.dumps('Tweet deleted successfully'),
            'headers': headers
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f'Internal Server Error: {str(e)}'),
            'headers': headers
        }
