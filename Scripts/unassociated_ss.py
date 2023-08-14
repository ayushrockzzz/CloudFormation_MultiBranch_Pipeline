from urllib import response
import boto3
import os
import pandas as pd
from datetime import date

client = boto3.client('ec2')
s3 = boto3.resource('s3')

date_today = date.today()
date_today = date_today.strftime("%Y,%m,%d")
date_today = date(int(date_today.split(',')[0]),int(date_today.split(',')[1]),int(date_today.split(',')[2]))

data={'Snapshot IDs(unassociated with AMI)':[]}

snapshot_response = client.describe_snapshots(OwnerIds=['self'])
snapshot_unassociated = []

def lambda_handler(event, context):
    aws_account_id = context.invoked_function_arn.split(":")[4]
    account_id = []
    for i in snapshot_response['Snapshots']:
        temp = ''
        temp = str(i['Description'])
        if(temp.find('ami-')==-1):
            snapshot_unassociated.append(i['SnapshotId'])
            account_id.append(aws_account_id)
    data['Account ID'] = account_id
    data['Snapshot IDs(unassociated with AMI)'] = snapshot_unassociated
    df=pd.DataFrame.from_dict(data)
    filename = 'UnassociatedSnapshots' + str(date_today) + '.csv'
    foldername = '/tmp/' + filename
    df.to_csv(foldername,index=None)
    filename = 'Automation-Reports/'+filename
    result = s3.meta.client.put_object(Body=open(foldername, 'rb'), Bucket=os.environ['BucketName'], Key=filename)
    res = result.get('ResponseMetadata')
    if res.get('HTTPStatusCode') == 200:
        print('File Uploaded Successfully')
    else:
        print('File Not Uploaded')