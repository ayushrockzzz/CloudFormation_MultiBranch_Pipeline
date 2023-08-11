#A cost optimization script
import boto3
import pandas as pd
from datetime import date
ec2_client = boto3.client('ec2')
s3 = boto3.resource('s3')
#fetching all the volumes
volumes = ec2_client.describe_volumes(Filters = [{'Name':'status','Values':['available']}])
# 
data={'Account ID':[],'Volume ID':[],'Free Space':[]}

date_today = date.today()
date_today = date_today.strftime("%Y,%m,%d")
date_today = date(int(date_today.split(',')[0]),int(date_today.split(',')[1]),int(date_today.split(',')[2]))
#fetching unused volumeIds
def lambda_handler(event, context):
    aws_account_id = context.invoked_function_arn.split(":")[4]
    account_id = []
    Size = []
    unused_vols_id = []
    for volume in volumes['Volumes']:
        temp = volume['VolumeId']
        unused_vols_id.append(temp)
        Size.append(volume['Size'])
        account_id.append(aws_account_id)
    data['Account ID'] = account_id
    data['Volume ID']=unused_vols_id
    data['Free Space'] = Size
    df=pd.DataFrame.from_dict(data)
    # df.to_csv('C:\\splunk-csv\\UnusedVolume.csv',index=None)
    filename = 'UnusedVolume' + str(date_today) + '.csv'
    foldername = '/tmp/' + filename
    df.to_csv(foldername,index=None)
    filename = 'Automation-Reports/'+filename
    result = s3.meta.client.put_object(Body=open(foldername, 'rb'), Bucket='automation-team-pranad-ayush-jayant-s3-backend', Key=filename)
    res = result.get('ResponseMetadata')
    if res.get('HTTPStatusCode') == 200:
        print('File Uploaded Successfully')
    else:
        print('File Not Uploaded')
