#A cost optimization script
import boto3
import pandas as pd
from datetime import date
import os


#if elastic ip is associated with any EC2 Instance instanceId will be present if elastic ip is not in use then InstanceID will not be there
date_today = date.today()
date_today = date_today.strftime("%Y,%m,%d")
date_today = date(int(date_today.split(',')[0]),int(date_today.split(',')[1]),int(date_today.split(',')[2]))

ec2 = boto3.client('ec2')
s3 = boto3.resource('s3')
response = ec2.describe_addresses()
data={'Unused Elastic IPs':[]}
unused_eips = []
def lambda_handler(event,context):
    aws_account_id = context.invoked_function_arn.split(":")[4]
    account_id = []
    for address in response['Addresses']:
        if 'InstanceId' not in address and 'AssociationId' not in address and 'NetworkInterfaceId' not in address:
            unused_eips.append(address['PublicIp'])
            account_id.append(aws_account_id)
    data['Account ID'] = account_id
    data['Unused Elastic IPs']=unused_eips
    df=pd.DataFrame.from_dict(data)

    filename = 'UnusedElasticIps' + str(date_today) + '.csv'
    foldername = '/tmp/' + filename
    df.to_csv(foldername,index=None)
    filename = 'Automation-Reports/'+filename
    result = s3.meta.client.put_object(Body=open(foldername, 'rb'), Bucket=os.environ['BucketName'], Key=filename)
    res = result.get('ResponseMetadata')
    if res.get('HTTPStatusCode') == 200:
        print('File Uploaded Successfully')
    else:
        print('File Not Uploaded')
    return{
            'message': 'success!!'
        }