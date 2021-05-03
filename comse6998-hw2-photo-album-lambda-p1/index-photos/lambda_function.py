import boto3
import base64
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import requests


def lambda_handler(event, context):
    # Test
    objectKey = event["Records"][0]["s3"]["object"]["key"]

    bucket = 'hw2-photos-s3-bucket-b2-cf'
    s3 = boto3.resource('s3')
    obj = s3.Object(bucket, objectKey)

    createdTimestamp = obj.get()['LastModified'].isoformat().replace("+00:00",
                                                                     "")
    labels = []
    if 'customlabels' in obj.get()['Metadata']:
        labels = obj.get()['Metadata']['customlabels'].lower()
        labels = labels.split(', ')

    photo = obj.get()['Body'].read().decode('utf-8')
    detect_labels = detect_labels_local_file(base64.b64decode(photo))

    if detect_has_face_local_file(base64.b64decode(photo)):
        if labels[-1] == 'name_label':
            my_bucket = s3.Bucket(bucket)
            client = boto3.client(
                'rekognition',
                region_name='us-east-1',
                aws_access_key_id='aws_access_key_id',
                aws_secret_access_key='aws_secret_access_key'
            )
            for file in my_bucket.objects.all():
                if objectKey == file.key:
                    continue

                obj2 = s3.Object(bucket, file.key)
                file_photo = obj2.get()['Body'].read().decode('utf-8')
                if detect_has_face_local_file(base64.b64decode(file_photo)):
                    response = client.compare_faces(
                        SourceImage={
                            'Bytes': base64.b64decode(photo)
                        },
                        TargetImage={
                            'Bytes': base64.b64decode(file_photo)
                        },
                        SimilarityThreshold=90
                    )
                    if response['FaceMatches']:
                        print('do something')
                        if 'customlabels' in obj2.get()['Metadata']:
                            labels2 = obj2.get()['Metadata'][
                                'customlabels'].lower()
                            labels2 = labels2.split(', ')
                            if labels2[-1] != 'name_label':
                                labels[-1] = labels2[-1]
                                break
            if labels[-1] == 'name_label':
                labels = labels[:-1]
    else:
        labels = labels[:-1]

    labels = list(set(labels) | set(detect_labels))

    for i in range(len(labels)):
        label = labels[i].strip()
        try:
            x = requests.get('https://api.datamuse.com/words?md=d&sp=' + label)
            r = x.json()
            if r:
                if "defHeadword" in r[0]:
                    label = r[0]["defHeadword"].lower()
                else:
                    label = r[0]["word"].lower()
        except:
            pass
        labels[i] = label

    labels = list(set(labels))
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


def detect_has_face_local_file(photo):
    # client = boto3.client('rekognition')
    client = boto3.client(
        'rekognition',
        region_name='us-east-1',
        aws_access_key_id='aws_access_key_id',
        aws_secret_access_key='aws_secret_access_key'
    )

    response = client.detect_faces(Image={'Bytes': photo},
                                   Attributes=['DEFAULT'])

    if response['FaceDetails']:
        return True
    else:
        return False


def index_photo_reference(json_object):
    host = 'search-photos-3hlik33wlntwau5muw5clt63ka.us-east-1.es.amazonaws.com'
    region = 'us-east-1'

    service = 'es'
    # credentials = boto3.Session().get_credentials()
    # awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region,
    #                     service, session_token=credentials.token)
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

    # # TODO implement
    # return {
    #     'statusCode': 200,
    #     'body': json.dumps('Hello from Lambda!')
    # }
