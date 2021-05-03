import json
import boto3
import uuid
from elasticsearch import Elasticsearch, RequestsHttpConnection, helpers
from requests_aws4auth import AWS4Auth
# import requests 
# from requests.auth import HTTPBasicAuth

def lambda_handler(event, context):
    query_text = event['queryStringParameters']['q'].strip().lower()
    # query_text = 'grass, bird, tree, flower'
    
    detect_search_keywords = ''
    if query_text and query_text != '':
        client = boto3.client('lex-runtime')
        response = client.post_text(
            botName='DetectSearchKeywordsBot',
            botAlias='DetectSearchKeywordsBot',
            userId=str(uuid.uuid1()),
            inputText=query_text
        )
    
        if 'slots' in response:
            for slot in response['slots'].values():
                if slot is not None:
                    detect_search_keywords += slot + ' '
                    
            if detect_search_keywords != '':
                detect_search_keywords = detect_search_keywords.strip()
        
    print(detect_search_keywords)
    
    # https://coralogix.com/log-analytics-blog/42-elasticsearch-query-examples-hands-on-tutorial/
    payload = {
        "query": {
            "match": {
                "labels": {
                    "query": detect_search_keywords
                }
            }
        }
    }
    
    host = 'search-photos-3hlik33wlntwau5muw5clt63ka.us-east-1.es.amazonaws.com'
    region = 'us-east-1'
    service = 'es'
    awsauth = AWS4Auth('', '', region, service)
    es = Elasticsearch(
        hosts=[{'host': host, 'port': 443}],
        http_auth=awsauth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection
        )
    
    res = helpers.scan(
        client = es,
        scroll = '2m',
        query = payload,
        index="photos")
    
    photo_url = []
    bucket = 'hw2-photos-s3-bucket-b2'
    for hit in res:
        objectKey = hit['_source']['objectKey']
        photo_url.append('https://' + bucket + '.s3.amazonaws.com/' + objectKey)
        
    # response = requests.post('https://search-photos-3hlik33wlntwau5muw5clt63ka.us-east-1.es.amazonaws.com/photos/_search', 
    #         auth = HTTPBasicAuth('Administrator', 'Columbia2021%'), json = payload)
    
    # photo_url = []
    # bucket = 'hw2-photos-s3-bucket-b2'
    # for hit in response.json()['hits']['hits']:
    #     objectKey = hit['_source']['objectKey']
    #     photo_url.append('https://' + bucket + '.s3.amazonaws.com/' + objectKey)
        
    # print(photo_url)
    
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        'body': json.dumps(photo_url)
    }
