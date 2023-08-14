import boto3
import datetime
from datetime import date
import csv
import os
 

date_today = date.today()
date_today = date_today.strftime("%Y,%m,%d")
date_today = date(int(date_today.split(',')[0]), int(date_today.split(',')[1]), int(date_today.split(',')[2]))

 

def lambda_handler(event, context):
    aws_account_id = context.invoked_function_arn.split(":")[4]
    account_id = []
    db_identity = []
    current_type = []
    suggested_type = []
    rds_client = boto3.client('rds')
    cloudwatch_client = boto3.client('cloudwatch')

 

    db_instances = rds_client.describe_db_instances()['DBInstances']

    for db_instance in db_instances:
        db_instance_identifier = db_instance['DBInstanceIdentifier']
        # Skip serverless instances
        if db_instance.get('DBInstanceClass') == 'db.serverless':
            print("{}".format(db_instance.get('DBInstanceClass')))
            continue

        # Get CPU utilization metrics from CloudWatch
        response = cloudwatch_client.get_metric_statistics(
            Namespace='AWS/RDS',
            MetricName='CPUUtilization',
            Dimensions=[{'Name': 'DBInstanceIdentifier', 'Value': db_instance_identifier}],
            StartTime=datetime.datetime.utcnow() - datetime.timedelta(minutes=10080),
            EndTime=datetime.datetime.utcnow(),
            Period=86400,  # 1 day
            Statistics=['Average']
        )
        if 'Datapoints' in response:
            datapoints = response['Datapoints']
            avg_cpu_utilization = sum([datapoint['Average'] for datapoint in datapoints]) / len(datapoints)
            suggested_instance_class = determine_suggested_instance_class(db_instance['DBInstanceClass'], avg_cpu_utilization)
            account_id.append(aws_account_id)
            db_identity.append(db_instance_identifier)
            current_type.append(db_instance['DBInstanceClass'])
            suggested_type.append(suggested_instance_class)
            print(f"DB Instance Identifier: {db_instance_identifier}, Suggested Instance Class: {suggested_instance_class}")
            
            
    filename = 'RDS-RightSizing-AIPowered' + str(date_today) + '.csv'
    foldername = '/tmp/' + filename
    with open(foldername, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['Account ID', 'DB Instance Identifier', 'Current Instance Class', 'Suggested Instance Class'])
        for i in range(0,len(account_id),1):
            csv_writer.writerow([account_id[i], db_identity[i], current_type[i], suggested_type[i]])

    s3_bucket_name = os.environ['BucketName']
    filename = 'Automation-Reports/' + filename
    upload_to_s3(foldername, s3_bucket_name, filename)

def determine_suggested_instance_class(current_instance_class, avg_cpu_utilization):
    instance_class_mapping = {
        'db.t2.micro': 1,
        'db.t2.small': 1,
        'db.t2.medium': 2,
        'db.m5.large': 2,
        'db.m5.xlarge': 4,
        'db.m5.2xlarge': 8,
        # Add more instance classes as needed
    }

    utilization_thresholds = [
        (10, 'db.t2.micro'),   # If utilization is below 10%, suggest db.t2.micro
        (20, 'db.t2.small'),   # If utilization is below 20%, suggest db.t2.small
        (30, 'db.t2.medium'),  # If utilization is below 30%, suggest db.t2.medium
        (50, 'db.m5.large'),   # If utilization is below 50%, suggest db.m5.large
        (70, 'db.m5.xlarge'),  # If utilization is below 70%, suggest db.m5.xlarge
        # Add more utilization thresholds and instance classes as needed
    ]


    for threshold, instance_class in utilization_thresholds:
        if avg_cpu_utilization < threshold and instance_class_mapping[instance_class] < instance_class_mapping[current_instance_class]:
            return instance_class
        elif avg_cpu_utilization > threshold and instance_class_mapping[instance_class] > instance_class_mapping[current_instance_class]:
            return instance_class
    return current_instance_class

def upload_to_s3(file_path, bucket_name, object_key):
    s3_client = boto3.client('s3')
    with open(file_path, 'rb') as file:
        s3_client.upload_fileobj(file, bucket_name, object_key)