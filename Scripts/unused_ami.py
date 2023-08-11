#A cost optimization script
import boto3
import pandas as pd
import datetime
from datetime import date
client = boto3.client('ec2')
s3 = boto3.resource('s3')

unused_amis = []
ami_age = []

data={'Account ID':[],'Unused AMI ID':[], 'AMI Age(days old)':[]}

#date time today
date_today = date.today()
date_today = date_today.strftime("%Y,%m,%d")
date_today = date(int(date_today.split(',')[0]),int(date_today.split(',')[1]),int(date_today.split(',')[2]))

response = client.describe_images(Owners=['self'],
    Filters=[
        {
            'Name': 'state',
            'Values': ['available']
        },
    ]
)

def lambda_handler(event,context):
    aws_account_id = context.invoked_function_arn.split(":")[4]
    account_id = []
    for i in response['Images']:
        temp = date(int(i['CreationDate'].split('T')[0].split('-')[0]),int(i['CreationDate'].split('T')[0].split('-')[1]),int(i['CreationDate'].split('T')[0].split('-')[2]))
        day_diff = (date_today-temp).days
        if(day_diff>3):
            unused_amis.append(i['ImageId'])
            ami_age.append(day_diff)
            account_id.append(aws_account_id)
    data['Account ID'] = account_id
    data['Unused AMI ID']=unused_amis
    data['AMI Age(days old)'] = ami_age
    df=pd.DataFrame.from_dict(data)
    # df.to_csv('\\UnusedAMI.csv',index=None)
    filename = 'UnusedAMI' + str(date_today) + '.csv'
    foldername = '/tmp/' + filename
    df.to_csv(foldername,index=None)
    # filename = filename + filename
    filename = 'Automation-Reports/'+filename
    result = s3.meta.client.put_object(Body=open(foldername, 'rb'), Bucket='automation-team-pranad-ayush-jayant-s3-backend', Key=filename)
    res = result.get('ResponseMetadata')
    if res.get('HTTPStatusCode') == 200:
        print('File Uploaded Successfully')
    else:
        print('File Not Uploaded')