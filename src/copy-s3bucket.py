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

TODOS - future enhancements
- check / determine if buckets exists source and destination; don't let boto3 throw on this
- improve total reporting on success/failure/attempt 
(do not fail on exceptions that can be handled in boto3/http - continue if single copy fails)
"""

import boto3
import argparse
import time
from botocore.exceptions import ClientError, BotoCoreError
from enum import Enum


def main():

    parser = argparse.ArgumentParser(prog="copy-s3bucket.py",
                                     description="Copies all files greater than the THRESHOLD size from SOURCE bucket to DESTINATION bucket ")
    # -required
    parser.add_argument("source_bucket", type=str,
                        help="Source S3 bucket name (e.g. 'sourcebucket')")
    parser.add_argument("destination_bucket", type=str,
                        help="Destination S3 bucket name (e.g. 'destinationbucket')")
    parser.add_argument("threshold", type=int,
                        help="Copy files larger than size specified.  Specify size in bytes as int. (e.g 1000)")
    parser.add_argument("-v", "--version", action="version", version="1.0")
    args = parser.parse_args()
    source_bucketname = args.source_bucket.strip()
    destination_bucketname = args.destination_bucket.strip()
    threshold_size = args.threshold

    try:
        # TODO replace below with auth() - wrap up in some checks - function?? stubbed...
        s3 = boto3.resource("s3")

        source_bucket = s3.Bucket(source_bucketname)
        destination_bucket = s3.Bucket(destination_bucketname)
        total = sum(1 for x in source_bucket.objects.all())

        print_message(message_type.INFO,
                      "S3 Bucket Source set to [{0}]".format(source_bucketname))
        print_message(message_type.INFO, "S3 Bucket Destination set to [{0}]".format(
            destination_bucketname))
        print_message(
            message_type.INFO, "Key/Object Size Threshold set to [{0} bytes] (must be at least this size)".format(threshold_size))
        print_message(
            message_type.INFO, "S3 Source Bucket Objects/Keys to attempt to copy [{0}]".format(total))

        failures = 0
        success = 0
        # print(total)
        timer = simple_timer()

        for src_obj in source_bucket.objects.all():
            # print(dir(obj))
            # print("------------")
            source = {'Bucket': source_bucketname, 'Key': src_obj.key}
            dest_key = src_obj.key
            if src_obj.size > threshold_size:
                destination_bucket.copy(source, dest_key)
                success += 1
                print_message(
                    message_type.INFO, "S3 Object/Key [{0}] with size: [{1} bytes] copied to destination".format(src_obj.key, src_obj.size))
            else:
                failures += 1
                print_message(message_type.WARNING, "S3 Object/Key [{0}] with size: [{1} bytes] did not meet requested threshold of "
                              "[{2} bytes].  Key NOT copied to destination".format(src_obj.key, src_obj.size, threshold_size))

        timer.stop()
        print_message(message_type.INFO, "[{5} copied] - Copied [{0}] keys out of total of [{1}] keys to the destination "
                      "bucket in [{2}]: [{3}] keys failed to meet threshold of [{4} bytes]".format(success, total, timer.print_summary(), failures, threshold_size, calculate_percentage(failures, total)))

    except Exception as e:
        print_message(message_type.ERROR,
                      "Error occurred [{0}] ".format(type(e).__name__), e)


def authenticate(aws_resource, region=None):
    ''' 
    Authenticate to AWS using boto3 session 
    Returns: boto3 client
    '''
    try:
        # do some checking of the env variables (if they exist)
        session = boto3.Session()
        client = session.client(aws_resource)
        print_message(message_type.INFO, "Using AWS ENV variable credentials via region [ {0} ]".format(
            session.region_name))
        return client
    except ClientError:
        raise
    except BotoCoreError:
        # boto3 / botocore exceptions are slim; this is the catchall :(
        raise


# ------------------
# - Helper functions/methods
# ------------------

class simple_timer(object):
    """ simple timer for util purposes """
    import time
    start_time = 0.0
    stop_time = 0.0
    elapsed = 0.0

    def __init__(self):
        self.start_time = time.time()

    def stop(self):
        self.stop_time = time.time()

    def get_elapsed(self):
        self.stop_time = time.time()
        self.elapsed = (self.stop_time - self.start_time)
        return self.elapsed

    def print_summary(self):
        return "{0} elapsed".format(time_from_float(self.elapsed))


def calculate_percentage(x, y):
    ''' 
    Calculates percentage given 2 ints (int, total)
    Returns: formatted string as percentage
    '''
    p = 0
    if(x is not 0):
        p = ((x / y) * 100)
    return ('{:.2f}%'.format(p))


def time_from_float(f):
    return time.strftime("%H:%M:%S", time.gmtime(f))


def print_message(message_type, friendly_message, detail_message="None"):
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
        print("{3}[{0}] - {1}{4}".format(str(message_type.name),
                                         friendly_message, detail_message, color, coloroff))
    else:
        print("{3}[{0}] - {1} - More Details [{2}]{4}".format(str(message_type.name),
                                                              friendly_message, detail_message, color, coloroff))


class message_type(Enum):
    """ Message type enumeration"""
    INVALID = 0
    DEBUG = 1
    INFO = 2
    WARNING = 3
    ERROR = 4


# Terminal color definitions - cheap and easy colors for this application
class Foreground:
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    RESET = '\033[39m'


class Background:
    BLACK = '\033[40m'
    RED = '\033[41m'
    GREEN = '\033[42m'
    YELLOW = '\033[43m'
    BLUE = '\033[44m'
    MAGENTA = '\033[45m'
    CYAN = '\033[46m'
    WHITE = '\033[47m'
    RESET = '\033[49m'


class Style:
    BRIGHT = '\033[1m'
    DIM = '\033[2m'
    NORMAL = '\033[22m'
    RESET_ALL = '\033[0m'


if __name__ == '__main__':
    main()
