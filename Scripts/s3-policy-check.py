import boto3
import botocore
import csv
from datetime import date,datetime,timedelta


date_today = date.today()
date_today = date_today.strftime("%Y,%m,%d")
date_today = date(int(date_today.split(',')[0]),int(date_today.split(',')[1]),int(date_today.split(',')[2]))

def lambda_handler(event, context):
    aws_account_id = context.invoked_function_arn.split(":")[4]
    filename = 'S3WithoutLifecycleConfiguration' + str(date_today) + '.csv'
    foldername = '/tmp/' + filename
    list_buckets_without_lifecycle_policy(foldername,aws_account_id)
    s3_bucket_name = 'automation-team-pranad-ayush-jayant-s3-backend'
    filename = 'Automation-Reports/'+filename
    upload_to_s3(foldername, s3_bucket_name, filename)

def list_buckets_without_lifecycle_policy(output_file,aws_account_id):
    s3_client = boto3.client('s3')
    response = s3_client.list_buckets()
    buckets = response['Buckets']
    buckets_without_lifecycle_data = []

    for bucket in buckets:
        bucket_name = bucket['Name']
        try:
            response = s3_client.get_bucket_lifecycle_configuration(Bucket=bucket_name)
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchLifecycleConfiguration':
                # Bucket does not have a lifecycle policy, add it to the list
                buckets_without_lifecycle_data.append((bucket_name))
    with open(output_file, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['Account ID','Bucket Name'])
        for bucket_name in buckets_without_lifecycle_data:
            csv_writer.writerow([aws_account_id,bucket_name])

def upload_to_s3(file_path, bucket_name, object_key):
    s3_client = boto3.client('s3')
    with open(file_path, 'rb') as file:
        s3_client.upload_fileobj(file, bucket_name, object_key)