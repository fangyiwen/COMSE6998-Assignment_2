import logging
import boto3
from botocore.exceptions import ClientError
import base64
import io
import csv


def upload_file(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True


# s3 = boto3.client('s3')
s3 = boto3.client(
    's3',
    region_name='us-east-1',
    aws_access_key_id='aws_access_key_id',
    aws_secret_access_key='aws_secret_access_key'
)
BUCKET_NAME = 'hw2-photos-s3-bucket-b2-cf'

filename_csv = "../photos/photo_table.csv"
rows = []
with open(filename_csv, 'r') as csvfile:
    csvreader = csv.reader(csvfile)
    fields = next(csvreader)
    for row in csvreader:
        rows.append(row)

for OBJECT_NAME, customLabels in rows:
    FILE_NAME = '../photos/' + OBJECT_NAME
    with open(FILE_NAME, "rb") as f:
        data = base64.b64encode(f.read())
        file = io.BytesIO(data)
        if customLabels != '':
            s3.upload_fileobj(file, BUCKET_NAME, OBJECT_NAME,
                              ExtraArgs={
                                  'Metadata': {'customLabels': customLabels},
                                  'ContentType': 'application/json'
                                  })
        else:
            s3.upload_fileobj(file, BUCKET_NAME, OBJECT_NAME,
                              ExtraArgs={
                                  'ContentType': 'application/json'
                              })
