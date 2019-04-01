#!/usr/local/bin/python3
"""
copy-s3bucket.py
-----------------------
Simple script that copies all files greater than the THRESHOLD size 
from SOURCE bucket to DESTINATION bucket 
-----------------------

Usage:
-----------------------
copy-s3bucket.py <source-bucketname> <destination-bucketname> <threshold>

Notes
-----------------------
Boto3 authenticates to AWS using Environment variables in this script.  
The variables that must be set before execution are as follows:

AWS_ACCESS_KEY_ID
The access key for your AWS account.
AWS_SECRET_ACCESS_KEY
The secret key for your AWS account.
AWS_DEFAULT_REGION
The region to use - defaults to 'us-west-2 if not provided

Assumes use of AWS credentials with S3FullAccess canned policy/permission ability for quick start
(should only need: source bucket (s3:Get*, s3:List*); destination bucket (s3:Get*, s3:List*, s3:Put*))

"""

import boto3
import argparse
from botocore.exceptions import ClientError, BotoCoreError
from enum import Enum

##########################################
#- Modify the options below as needed
##########################################

DEFAULT_REGION="us-west-2"

##########################################
#- END - Do not modify below here!!!
##########################################

def main():

    parser = argparse.ArgumentParser(prog="copy-s3bucket.py", \
            description="Copies all files greater than the THRESHOLD size from SOURCE bucket to DESTINATION bucket ")
    #-required
    parser.add_argument("source_bucket", type=str, \
            help="Source S3 bucket name (e.g. 'sourcebucket')")
    parser.add_argument("destination_bucket", type=str, \
            help="Destination S3 bucket name (e.g. 'destinationbucket')")
    parser.add_argument("threshold", type=int, \
            help="Copy files larger than size specified.  Specify size in bytes as int. (e.g 1000)")
    #-informational args
    # parser.add_argument("-d", "--debug", action="store_true",
    #         help="Debug mode - show more informational messages for debugging")
    parser.add_argument("-v", "--version", action="version", version="1.0")
    args = parser.parse_args()
    source_bucketname = args.source_bucket.strip()
    destination_bucketname = args.destination_bucket.strip()
    threshold_size = args.threshold

    try:
        #auth - wrap up in some checks - function??
        #set threshold
        #determine if buckets exists source and destination
        #copy all contents/keys - source to destination bucket, based on threshold - track count and amt??
        #print total of amt copied/ messages etc

        s3 = boto3.resource("s3")
        source_bucket = s3.Bucket(source_bucketname)
        destination_bucket = s3.Bucket(destination_bucketname)

        print_message(message_type.DEBUG,"S3 Bucket Source set to [{0}]".format(source_bucketname))
        print_message(message_type.INFO,"S3 Bucket Destination set to [{0}]".format(destination_bucketname))

        for src_obj in source_bucket.objects.all():
            #print(dir(obj))
            #print("------------")
            source = { 'Bucket': source_bucketname, 'Key': src_obj.key}
            dest_key = src_obj.key
            destination_bucket.copy(source,dest_key)

            print_message(message_type.INFO,"S3 Object/Key [{0}] with size: [{1} bytes] copied to destination".format(src_obj.key,src_obj.size))
           
    except Exception as e:
        print_message(message_type.ERROR,"Error occurred [{0}] ".format(type(e).__name__),e)


def authenticate(aws_resource, region=None):
    ''' 
    Authenticate to AWS using boto3 session 
    Returns: boto3 client
    '''
    try:
        #do some checking of the env variables (if they exist)
        session = boto3.Session()
        client = session.client(aws_resource)
        print_message(message_type.INFO,"Using AWS ENV variable credentials via region [ {0} ]".format(session.region_name))
        return client
    except ClientError:
        raise 
    except BotoCoreError:
        #boto3 / botocore exceptions are slim; this is the catchall :(
        raise 


# ------------------
# - Helper functions/methods
# ------------------

def print_message(message_type,friendly_message,detail_message="None"):
    """ prints messages in format we want """
    if message_type == message_type.DEBUG:
        color = Foreground.YELLOW
        coloroff = Style.RESET_ALL
    elif message_type == message_type.INFO:
        color = Foreground.GREEN
        coloroff = Style.RESET_ALL
    elif message_type == message_type.WARNING:
        color = Foreground.YELLOW
        coloroff = Style.RESET_ALL
    elif message_type == message_type.ERROR:
        color = Foreground.RED
        coloroff = Style.RESET_ALL
    else:
        color = ""
        coloroff = ""
    if detail_message == "None":
        print("{3}[{0}] - {1}{4}".format(str(message_type.name),friendly_message,detail_message,color,coloroff))
    else:
        print("{3}[{0}] - {1} - More Details [{2}]{4}".format(str(message_type.name),friendly_message,detail_message,color,coloroff))


class message_type(Enum):
    """ Message type enumeration"""
    INVALID = 0
    DEBUG = 1
    INFO = 2
    WARNING = 3
    ERROR = 4


# Terminal color definitions - cheap and easy colors for this application
class Foreground:
    BLACK   = '\033[30m'
    RED     = '\033[31m'
    GREEN   = '\033[32m'
    YELLOW  = '\033[33m'
    BLUE    = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN    = '\033[36m'
    WHITE   = '\033[37m'
    RESET   = '\033[39m'

class Background:
    BLACK   = '\033[40m'
    RED     = '\033[41m'
    GREEN   = '\033[42m'
    YELLOW  = '\033[43m'
    BLUE    = '\033[44m'
    MAGENTA = '\033[45m'
    CYAN    = '\033[46m'
    WHITE   = '\033[47m'
    RESET   = '\033[49m'

class Style:
    BRIGHT    = '\033[1m'
    DIM       = '\033[2m'
    NORMAL    = '\033[22m'
    RESET_ALL = '\033[0m'

if __name__ == '__main__':
    main()


