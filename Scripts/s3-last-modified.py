import boto3
import csv
from datetime import date
from datetime import datetime
import pandas as pd

client=boto3.client("s3")
s3 = boto3.resource('s3')

date_today = datetime.today()

def lambda_handler(event, context):
    account_id = []
    aws_account_id = context.invoked_function_arn.split(":")[4]
    s3_name = []
    s3_date = []
    data={'Account ID':[],'S3 Name':[], 'Last Modified Date': []}
    response = client.list_buckets(Owner = ['self'])
    for bucket in response['Buckets']:
        bucket_name = bucket['Name']
        try:
            objects = client.list_objects(Bucket=bucket_name)
        except:
            break
        contents = objects.get('Contents')
        if contents is not None:
            for obj in contents:
                date = obj['LastModified']
                fol = bucket_name
                key = fol
                lmd = date
                lmd = str(lmd).split(' ')[0]
            date_format = "%Y-%m-%d"
            temp = datetime.strptime(lmd,date_format)
            day_diff = (date_today-temp).days
            if(day_diff>=180):
                s3_name.append(key)
                s3_date.append(temp)
                account_id.append(aws_account_id)
    data['Account ID'] = account_id
    data['S3 Name'] = s3_name
    data['Last Modified Date'] = s3_date
    df= pd.DataFrame.from_dict(data)
    filename = 'S3LastModified' + str(date_today.strftime('%Y-%m-%d')) + '.csv'
    foldername = '/tmp/' + filename
    df.to_csv(foldername,index=None)
    filename = 'Automation-Reports/'+filename
    result = s3.meta.client.put_object(Body=open(foldername, 'rb'), Bucket='automation-team-pranad-ayush-jayant-s3-backend', Key=filename)
    res = result.get('ResponseMetadata')
    if res.get('HTTPStatusCode') == 200:
        print('File Uploaded Successfully')
    else:
        print('File Not Uploaded')
    return{
            'message': 'success!!'
        }