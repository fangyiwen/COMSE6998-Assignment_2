import boto3

client = boto3.client(
    'lex-models',
    region_name='us-east-1',
    aws_access_key_id='aws_access_key_id',
    aws_secret_access_key='aws_secret_access_key'
)

response = client.delete_bot_version(
    name='DetectSearchKeywordsBot',
    version='7'
)

print(response)
