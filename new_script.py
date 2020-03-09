#!/usr/bin/env python3

import boto3
import sys
import requests
import time
#cloudwatch import date 
from datetime import datetime, timedelta

#config file variable import
from config import ImageVAR
from config import SecurityGroupVAR
from config import KeyNameVAR
from config import startscriptVAR


#bucket name entry for s3
bucket_name = input("Please enter your desired bucket name: ")


#launch ec2 instance
print("launching your ec2 instance now...")
time.sleep(2)
ec2 = boto3.resource('ec2')
instance = ec2.create_instances(
  MinCount = 1,
  MaxCount = 1,
  ImageId = ImageVAR,
  SecurityGroupIds = SecurityGroupVAR,
  KeyName = KeyNameVAR,
  Monitoring = {
    'Enabled': True
  },
  TagSpecifications=[
        {
            'ResourceType': 'instance',
            'Tags': [
                {
                    'Key': 'Owner',
                    'Value': 'Rory'
                },
            ]
        },
    ],
  UserData = startscriptVAR,
  InstanceType = 't2.nano')

print("")  
print("Instance created: ",instance[0].id)

#launch bucket
s3 = boto3.resource("s3")

try:
   response = s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={'LocationConstraint': 'eu-west-1'})
   #print (response)
   time.sleep(2)
   print ("Your s3 bucket has been created successfully: ", response)
except Exception as error:
  print (error)


  #launch cloudwatch
cloudwatch = boto3.resource('cloudwatch')
print("")
print("Your cloudwatch statistics will be availible in 10 minutes...")
time.sleep(5)
print("sit tight!")


#time allows the instance and monitoring to be fully enabled
time.sleep(600)
print ("Starting cloudwatch monitoring...")
instid = instance[0].id
print ("Monitoring your Current instance ID: ", instid)


#ec2 instance cloudwatch cpu
#fetch latest instance ID
instance = ec2.Instance(instid)
instance.monitor()       # Enables detailed monitoring on instance (1-minute intervals)

metric_iterator = cloudwatch.metrics.filter(Namespace='AWS/EC2',
                                            MetricName='CPUUtilization',
                                            Dimensions=[{'Name':'InstanceId', 'Value': instid}])

metric = list(metric_iterator)[0]    # extract first (only) element

response = metric.get_statistics(StartTime = datetime.utcnow() - timedelta(minutes=5),   # 5 minutes ago
                                 EndTime=datetime.utcnow(),                              # now
                                 Period=300,                                             # 5 min intervals
                                 Statistics=['Average'])

print ("Average CPU utilisation:", response['Datapoints'][0]['Average'], response['Datapoints'][0]['Unit'])





