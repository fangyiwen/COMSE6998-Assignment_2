import base64
import boto3
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth


def lambda_handler(event, context):
    # objectKey = event["Records"][0]["s3"]["object"]["key"]
    objectKey = 'dog_1.jpg'

    bucket = 'hw2-photos-s3-bucket-b2'

    # s3 = boto3.resource('s3')
    s3 = boto3.resource(
        's3',
        region_name='us-east-1',
        aws_access_key_id='aws_access_key_id',
        aws_secret_access_key='aws_secret_access_key'
    )

    obj = s3.Object(bucket, objectKey)

    createdTimestamp = obj.get()['LastModified'].isoformat().replace("+00:00",
                                                                     "")
    labels = obj.get()['Metadata']['customlabels'].lower()
    labels = labels.split(', ')
    photo = obj.get()['Body'].read().decode('utf-8')
    detect_labels = detect_labels_local_file(base64.b64decode(photo))
    labels = list(set(labels) | set(detect_labels))

    json_object = {'objectKey': objectKey,
                   'bucket': bucket,
                   'createdTimestamp': createdTimestamp,
                   'labels': labels}

    index_photo_reference(json_object)


def detect_labels_local_file(photo):
    # client = boto3.client('rekognition')
    client = boto3.client(
        'rekognition',
        region_name='us-east-1',
        aws_access_key_id='aws_access_key_id',
        aws_secret_access_key='aws_secret_access_key'
    )

    response = client.detect_labels(Image={'Bytes': photo})

    res = []
    for label in response['Labels']:
        res.append(label['Name'].lower())

    return res


def index_photo_reference(json_object):
    host = 'search-photos-3hlik33wlntwau5muw5clt63ka.us-east-1.es.amazonaws.com'
    region = 'us-east-1'

    service = 'es'
    # credentials = boto3.Session().get_credentials()
    # awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region,
    #                    service, session_token=credentials.token)
    awsauth = AWS4Auth('aws_access_key_id',
                       'aws_secret_access_key', region,
                       service)

    es = Elasticsearch(
        hosts=[{'host': host, 'port': 443}],
        http_auth=awsauth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection
    )

    document = json_object

    es.index(index="photos", doc_type="photo", id=document['objectKey'],
             body=document)

    print(es.get(index="photos", doc_type="photo", id=document['objectKey']))


lambda_handler(None, None)
