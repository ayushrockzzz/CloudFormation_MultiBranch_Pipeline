import boto3
import csv
import os
from datetime import date
date_today = date.today()
date_today = date_today.strftime("%Y,%m,%d")
date_today = date(int(date_today.split(',')[0]),int(date_today.split(',')[1]),int(date_today.split(',')[2]))

account_id = []

def lambda_handler(event, context):
    aws_account_id = context.invoked_function_arn.split(":")[4]
    filename = 'UnusedEFS' + str(date_today) + '.csv'
    foldername = '/tmp/' + filename
    unused_volumes_file = list_unused_efs_volumes(foldername,aws_account_id)
    s3_bucket_name = 'automation-team-pranad-ayush-jayant-s3-backend'
    filename = 'Automation-Reports/'+filename
    upload_to_s3(unused_volumes_file, s3_bucket_name, filename)
    
def list_unused_efs_volumes(output_file,aws_account_id):
    # Initialize Boto3 clients for EFS and EC2
    efs_client = boto3.client('efs')
    ec2_client = boto3.client('ec2')

    # List all EFS file systems
    response = efs_client.describe_file_systems()
    file_systems = response['FileSystems']
    
    # Retrieve all EFS volumes that are in use
    used_volumes = set()
    instances = ec2_client.describe_instances()
    for reservation in instances['Reservations']:
        for instance in reservation['Instances']:
            for block_device in instance.get('BlockDeviceMappings', []):
                if 'Ebs' in block_device and 'VolumeId' in block_device['Ebs']:
                    used_volumes.add(block_device['Ebs']['VolumeId'])
                    
    # Find and write unused EFS volumes to CSV file
    unused_volumes = [fs['FileSystemId'] for fs in file_systems if fs['FileSystemId'] not in used_volumes]
    with open(output_file, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['Account ID','Unused EFS Volumes'])
        for volume_id in unused_volumes:
            csv_writer.writerow([aws_account_id,volume_id])
    return output_file

def upload_to_s3(file_path, bucket_name, object_key):
    s3_client = boto3.client('s3')
    with open(file_path, 'rb') as file:
        s3_client.upload_fileobj(file, bucket_name, object_key)