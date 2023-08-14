from difflib import Differ
from ipaddress import ip_address
import boto3
import pandas as pd
from datetime import datetime
from datetime import date
import os


client=boto3.client('ec2')
resp=client.describe_instances(Filters=[{'Name':'instance-state-name','Values':['stopped']}])
date_today = date.today()
date_today = date_today.strftime("%Y,%m,%d")
date_today = date(int(date_today.split(',')[0]),int(date_today.split(',')[1]),int(date_today.split(',')[2]))
s3 = boto3.resource('s3')
ses_client = boto3.client('ses')
instance_name = []
instance_id = []
Diff_List=[]
ip_address_list = []

def lambda_handler(event, context):
    account_id = []
    aws_account_id = context.invoked_function_arn.split(":")[4]
    for i in resp['Reservations']:
        for j in i['Instances']:
            InstanceId = j['InstanceId']
            try:
                InstanceTime = j['StateTransitionReason'].split('(')[1].split(' ')[0]
            except:
                break
            temp = date(int(InstanceTime.split('-')[0]),int(InstanceTime.split('-')[1]),int(InstanceTime.split('-')[2]))
            day_diff = (date_today-temp).days
            if day_diff>=14:
                instance_id.append(InstanceId)
                Diff_List.append(day_diff)
                ip_address_list.append(j['PrivateIpAddress'])
                account_id.append(aws_account_id)
                try:
                    for k in j['Tags']:
                        try:
                            if k['Key']=='Name':
                                instance_name.append(k['Value'])
                                break
                        except:
                            break
                except:
                    instance_name.append('--')
    data={'Account ID':[],'Instance Name':[],'Instance ID':[],'Private IP': [],'Instance is Stopped from(days)':[]}
    data['Account ID'] = account_id
    data['Instance Name'] = instance_name
    data['Instance ID']=instance_id
    data['Private IP'] = ip_address_list
    data['Instance is Stopped from(days)']=Diff_List
    df=pd.DataFrame.from_dict(data)
    filename = 'StoppedInstances' + str(date_today) + '.csv'
    foldername = '/tmp/' + filename
    df.to_csv(foldername,index=None)
    filename = 'Automation-Reports/'+filename
    result = s3.meta.client.put_object(Body=open(foldername, 'rb'), Bucket=os.environ['BucketName'], Key=filename)
    res = result.get('ResponseMetadata')
    if res.get('HTTPStatusCode') == 200:
        print('File Uploaded Successfully')
    else:
        print('File Not Uploaded')