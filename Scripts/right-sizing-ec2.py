import boto3
import datetime
from datetime import date
import csv
import os

date_today = date.today()
date_today = date_today.strftime("%Y,%m,%d")
date_today = date(int(date_today.split(',')[0]),int(date_today.split(',')[1]),int(date_today.split(',')[2]))

def lambda_handler(event, context):
    aws_account_id = context.invoked_function_arn.split(":")[4]
    account_id = []
    ec2_identity = []
    current_type = []
    suggested_type = []
    ec2_client = boto3.client('ec2')
    cloudwatch_client = boto3.client('cloudwatch')

    instance_list = ec2_client.describe_instances(Filters=[{
        'Name': 'instance-state-name',
        'Values': ['running']}])['Reservations']

    for reservation in instance_list:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']

            # Get CPU utilization metrics from CloudWatch
            response = cloudwatch_client.get_metric_statistics(
                Namespace='AWS/EC2',
                MetricName='CPUUtilization',
                Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
                StartTime=datetime.datetime.utcnow() - datetime.timedelta(minutes=10080),
                EndTime=datetime.datetime.utcnow(),
                Period=86400,  # 1 day
                Statistics=['Average']
            )

            if 'Datapoints' in response:
                datapoints = response['Datapoints']
                avg_cpu_utilization = sum([datapoint['Average'] for datapoint in datapoints]) / len(datapoints)
                suggested_instance_type = determine_suggested_instance_type(instance['InstanceType'], avg_cpu_utilization)
                # suggested_instance_type = determine_suggested_instance_type('t2.medium', 10.0)
                account_id.append(aws_account_id)
                ec2_identity.append(str(instance_id))
                current_type.append(instance['InstanceType'])
                suggested_type.append(suggested_instance_type)
                print(f"Instance ID: {instance_id}, Suggested Instance Type: {suggested_instance_type}")

                
    filename = 'EC2-RightSizing-AIPowered' + str(date_today) + '.csv'
    foldername = '/tmp/' + filename
    with open(foldername, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['Account ID','Instance ID', 'Current Instance Type','Suggested Instance Type'])
        for i in range(0,len(account_id),1):
            csv_writer.writerow([account_id[i],ec2_identity[i], current_type[i],suggested_type[i]])
                    
    s3_bucket_name = os.environ['BucketName']
    filename = 'Automation-Reports/'+filename
    upload_to_s3(foldername, s3_bucket_name, filename)

def determine_suggested_instance_type(current_instance_type, avg_cpu_utilization):
   # Define a mapping of instance types and their corresponding vCPUs
    instance_type_mapping = {
       't2.micro': 1,
       't2.small': 1,
       't2.medium': 2,
       'm5.large': 2,
       'm5.xlarge': 4,
       'm5.2xlarge': 8,
       # Add more instance types as needed
    }

   # Define utilization thresholds and their corresponding recommended instance types
    utilization_thresholds = [
       (10, 't2.micro'),   # If utilization is below 10%, suggest t2.micro
       (20, 't2.small'),   # If utilization is below 20%, suggest t2.small
       (30, 't2.medium'),  # If utilization is below 30%, suggest t2.medium
       (50, 'm5.large'),   # If utilization is below 50%, suggest m5.large
       (70, 'm5.xlarge'),  # If utilization is below 70%, suggest m5.xlarge
       # Add more utilization thresholds and instance types as needed
    ]

    for threshold, instance_type in utilization_thresholds:
    #   print("Threshold: {}, Instance Type: {}".format(threshold,instance_type))
        print(threshold)
        if avg_cpu_utilization < threshold and instance_type_mapping[instance_type] < instance_type_mapping[current_instance_type]:
            # print('Hi in 1st if')
            return instance_type
        elif(avg_cpu_utilization > threshold and instance_type_mapping[instance_type] > instance_type_mapping[current_instance_type]):
            # print('Hi in 2nd if')
            return instance_type  
    return current_instance_type

def upload_to_s3(file_path, bucket_name, object_key):
    s3_client = boto3.client('s3')
    with open(file_path, 'rb') as file:
        s3_client.upload_fileobj(file, bucket_name, object_key)
