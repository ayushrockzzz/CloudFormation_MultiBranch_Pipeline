import boto3
import csv
import datetime
from datetime import date,datetime,timedelta


date_today = date.today()
date_today = date_today.strftime("%Y,%m,%d")
date_today = date(int(date_today.split(',')[0]),int(date_today.split(',')[1]),int(date_today.split(',')[2]))

def lambda_handler(event, context):
    aws_account_id = context.invoked_function_arn.split(":")[4]
    filename = 'Unused-RDS' + str(date_today) + '.csv'
    foldername = '/tmp/' + filename
    list_unused_stopped_rds_instances(foldername,aws_account_id)
    s3_bucket_name = 'automation-team-pranad-ayush-jayant-s3-backend'
    filename = 'Automation-Reports/'+filename
    upload_to_s3(foldername, s3_bucket_name, filename)
    
def list_unused_stopped_rds_instances(output_file, aws_account_id):
    # Initialize Boto3 client for RDS
    rds_client = boto3.client('rds')

    # Calculate the date one week ago
    one_week_ago = datetime.now() - timedelta(weeks=1)

    # List all RDS instances
    response = rds_client.describe_db_instances()
    db_instances = response['DBInstances']

    # Find unused instances in "stopped" state and write to CSV file
    unused_stopped_instances_data = []

    for instance in db_instances:
        if instance['DBInstanceStatus'] == 'stopped':
            instance_creation_time = instance['InstanceCreateTime']
            if instance_creation_time < one_week_ago:
                unused_stopped_instances_data.append((
                    instance['DBInstanceIdentifier'],
                    instance['DBInstanceClass'],
                    instance['Engine'],
                    instance['EngineVersion'],
                    instance['AllocatedStorage'],
                    instance['AvailabilityZone']
                ))

    with open(output_file, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['Account ID','Instance Identifier', 'Instance Class', 'Engine', 'Engine Version', 'Allocated Storage', 'Availability Zone'])
        for instance_id, instance_class, engine, engine_version, allocated_storage, availability_zone in unused_stopped_instances_data:
            csv_writer.writerow([aws_account_id,instance_id, instance_class, engine, engine_version, allocated_storage, availability_zone])

def upload_to_s3(file_path, bucket_name, object_key):
    s3_client = boto3.client('s3')
    with open(file_path, 'rb') as file:
        s3_client.upload_fileobj(file, bucket_name, object_key)