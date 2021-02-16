#Simon Aronsky
#02/14/2020
#Backup.py

import boto3
import os
from botocore.exceptions import ClientError
import datetime
import pytz
import sys

def recurseDirectory(sysPath, awsPath, s3, bucketName):
    for dir in os.listdir(sysPath):
        update=False
        isDir=os.path.isdir(sysPath+dir)
        if isDir and dir[-1]!="/":
            dir=dir+"/"
        try:
            object = boto3.client("s3").get_object(Bucket=bucketName, Key=awsPath + dir)
            if object["LastModified"] < datetime.datetime.fromtimestamp(os.path.getmtime(sysPath + dir)).astimezone(
                    pytz.utc):
                update = True
        except ClientError as ex:
            if ex.response['Error']['Code'] == "NoSuchKey":
                update = True
        if isDir:
            recurseDirectory(sysPath+dir, awsPath+dir,s3, bucketName)
        elif update:
            print("UPDATING: "+sysPath + dir)
            s3.upload_file(sysPath+dir, bucketName, awsPath+dir)

s3=boto3.client("s3")
path=sys.argv[1]
bucketName=sys.argv[2].split("::")[0]
bucketDirectory=sys.argv[2].split("::")[1]
os.chdir(path)
try:
    response= s3.create_bucket(Bucket=bucketName)
except ClientError as e:
    print(e.response['Error']['Code'])
recurseDirectory(path, bucketDirectory,s3, bucketName)