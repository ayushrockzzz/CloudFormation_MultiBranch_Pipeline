import boto3
import csv
import datetime
from datetime import date,datetime,timedelta
import os


date_today = date.today()
date_today = date_today.strftime("%Y,%m,%d")
date_today = date(int(date_today.split(',')[0]),int(date_today.split(',')[1]),int(date_today.split(',')[2]))

def lambda_handler(event, context):
    aws_account_id = context.invoked_function_arn.split(":")[4]
    filename = 'Underutilized-RDS' + str(date_today) + '.csv'
    foldername = '/tmp/' + filename
    list_underutilized_rds_instances(foldername,aws_account_id)
    s3_bucket_name = os.environ['BucketName']
    filename = 'Automation-Reports/'+filename
    upload_to_s3(foldername, s3_bucket_name, filename)
    
def list_underutilized_rds_instances(output_file,aws_account_id):
    # Initialize Boto3 clients for RDS and CloudWatch
    rds_client = boto3.client('rds')
    cloudwatch_client = boto3.client('cloudwatch')

    # Get list of RDS instances
    response = rds_client.describe_db_instances()
    db_instances = response['DBInstances']

    # Calculate the time range for the past week
    end_time = datetime.now()
    start_time = end_time - timedelta(days=7)

    # Find underutilized RDS instances
    underutilized_instances = []

    for db_instance in db_instances:
        db_identifier = db_instance['DBInstanceIdentifier']
        
        # Retrieve CPU utilization metrics for the past week
        response = cloudwatch_client.get_metric_statistics(
            Namespace='AWS/RDS',
            MetricName='CPUUtilization',
            Dimensions=[
                {'Name': 'DBInstanceIdentifier', 'Value': db_identifier}
            ],
            StartTime=start_time,
            EndTime=end_time,
            Period=3600,  # 1-hour granularity
            Statistics=['Average']
        )

        # Calculate average CPU utilization
        if 'Datapoints' in response:
            datapoints = response['Datapoints']
            total_utilization = sum(dp['Average'] for dp in datapoints)
            average_utilization = total_utilization / len(datapoints)
            
            # Check if the average utilization is less than 20%
            if average_utilization < 20:
                underutilized_instances.append((db_identifier, average_utilization))

    # Write underutilized instances to CSV file
    with open(output_file, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['Account ID','Underutilized RDS Instances', 'Average CPU Utilization (%)'])
        for db_identifier, average_utilization in underutilized_instances:
            csv_writer.writerow([aws_account_id,db_identifier, average_utilization])
            
def upload_to_s3(file_path, bucket_name, object_key):
    s3_client = boto3.client('s3')
    with open(file_path, 'rb') as file:
        s3_client.upload_fileobj(file, bucket_name, object_key)