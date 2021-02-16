#Simon Aronsky
#02/14/2020
#Restore.py

import boto3
import os
import sys
from botocore.exceptions import ClientError

def recurseDirectoryCreation(sysPath, stringKey, s3, bucketName):
    dirIndex = stringKey.find("/")
    if (dirIndex != -1):
        dir=stringKey[0:dirIndex]
        if not os.path.isdir(sysPath + dir):
            print("Making Directory: "+sysPath+dir)
            os.mkdir(sysPath+dir)
        return recurseDirectoryCreation(sysPath+dir+"/", stringKey[dirIndex+1:], s3, bucketName)
    else:
        os.chdir(sysPath)
        return stringKey

bucketName=sys.argv[1].split("::")[0]
bucketDirectory=sys.argv[1].split("::")[1]
path=sys.argv[2]
s3 = boto3.client("s3")
if not (os.path.isdir(path)):
    os.mkdir(path)
os.chdir(path)
if bucketDirectory:
    keys = s3.list_objects(Bucket=bucketName, Delimiter='string', Prefix=bucketDirectory)
else:
    keys = s3.list_objects(Bucket=bucketName, Delimiter='string')
for key in keys["Contents"]:
    os.chdir(path)
    stringKeyFull = key["Key"]
    stringKey=recurseDirectoryCreation(path, stringKeyFull, s3, bucketName)
    if stringKey:
        print(stringKey)
        with open(stringKey, 'wb') as data:
            try:
                print("Restoring: "+stringKeyFull)
                s3.download_fileobj(bucketName, stringKeyFull, data)
            except ClientError as e:
                print(e)
                print(stringKey)