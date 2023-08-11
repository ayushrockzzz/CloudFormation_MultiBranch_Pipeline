import boto3
import csv
import datetime
from datetime import date,datetime,timedelta


date_today = date.today()
date_today = date_today.strftime("%Y,%m,%d")
date_today = date(int(date_today.split(',')[0]),int(date_today.split(',')[1]),int(date_today.split(',')[2]))

def lambda_handler(event, context):
    aws_account_id = context.invoked_function_arn.split(":")[4]
    filename = 'CWExpirationCheck' + str(date_today) + '.csv'
    foldername = '/tmp/' + filename
    list_log_groups_without_retention_policy(foldername,aws_account_id)
    s3_bucket_name = 'automation-team-pranad-ayush-jayant-s3-backend'
    filename = 'Automation-Reports/'+filename
    upload_to_s3(foldername, s3_bucket_name, filename)

    
def list_log_groups_without_retention_policy(output_file, aws_account_id):
    # Initialize Boto3 client for CloudWatch Logs
    logs_client = boto3.client('logs')

    # Describe all log groups
    response = logs_client.describe_log_groups()
    log_groups = response['logGroups']

    # Find log groups without a retention policy and write to CSV file
    log_groups_without_retention_data = []

    for log_group in log_groups:
        if 'retentionInDays' not in log_group:
            log_groups_without_retention_data.append((log_group['logGroupName']))

    with open(output_file, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['Account ID','Log Group Name'])
        for log_group_name in log_groups_without_retention_data:
            csv_writer.writerow([aws_account_id,log_group_name])
            
def upload_to_s3(file_path, bucket_name, object_key):
    s3_client = boto3.client('s3')
    with open(file_path, 'rb') as file:
        s3_client.upload_fileobj(file, bucket_name, object_key)