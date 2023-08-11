#Script for cost optimization; to check weekly avg cpu utilization per instance.
import boto3
import datetime
from datetime import date
import pandas as pd
import os

def lambda_handler(event, context):
    aws_account_id = context.invoked_function_arn.split(":")[4]
    account_id = []
    cw = boto3.client('cloudwatch')
    client = boto3.client('ec2')
    s3 = boto3.resource('s3')
    resp = client.describe_instances(Filters=[{
        'Name': 'instance-state-name',
        'Values': ['running']
    }])

    date_today = date.today()
    date_today = date_today.strftime("%Y,%m,%d")
    date_today = date(int(date_today.split(',')[0]),int(date_today.split(',')[1]),int(date_today.split(',')[2]))

    InstanceIdList = []
    for reservation in resp['Reservations']:
        for instance in reservation['Instances']:
            InstanceIdList.append(instance['InstanceId'])

    instance_id_list = []
    utilization_list = []

    for i in InstanceIdList:
        instance_id_list.append(i)
        Id = i
        result = cw.get_metric_statistics(
                Period=86400,
                StartTime=datetime.datetime.utcnow() - datetime.timedelta(minutes=10080),
                EndTime=datetime.datetime.utcnow(),
                MetricName='CPUUtilization',
                Namespace='AWS/EC2',
                Statistics=['Average'],
                Dimensions=[{'Name': 'InstanceId', 'Value': Id}]
        )
        dp = result['Datapoints']
        m = len(dp)
        sumavg = 0
        for j in range(0, m):
            a = dp[j]
            avg = a['Average']
            sumavg = sumavg + avg
        weekAvg = sumavg/7
        weekAvg = "{:.2f}".format(float(weekAvg))
        if float(weekAvg)<20.00:
            utilization_list.append(str(weekAvg) + '%')
            account_id.append(aws_account_id)
    df = pd.DataFrame({'Account ID': account_id,'Instance ID': instance_id_list, 'Weekly Average CPU Utilization <20%': utilization_list})
    filename = 'UnderUtilized-EC2' + str(date_today) + '.csv'
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
        'msg':'success!'
    }