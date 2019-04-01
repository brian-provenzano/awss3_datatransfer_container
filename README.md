## AWS S3 Bucket Data Copy Container
This repo contains a containerized python script/application that when given the names of two S3 buckets (source, destination) and a threshold size in MB, will copy all files greater than the threshold size from the  source bucket to the destination bucket.  Assumptions are that the buckets are in the same region and the AWS credentials used by the script have the proper permissions/policies applied to allow the copy.


## Prerequisites
- [AWS Account](https://aws.amazon.com/free/?nc2=h_ql_pr) - free tier can be utilized
- [AWS Credentials](https://docs.aws.amazon.com/sdk-for-java/v1/developer-guide/signup-create-iam-user.html) - Ensure your IAM user has the correct permissions (S3FullAccess should be enough) and you have created API credentials for use.  We will use API credentials (access key, secret key) set as ENV variables.
- [Docker](https://docs.docker.com/install/)  - install docker for your operating system.  Tested on Fedora 29 (Linux), but should work on latest supported versions of Docker CE on any platform.
- [Python](https://www.python.org)  - if testing locally (outside the docker image) you will need python 3 (validated on 3.7.x).  This should not be necessary as our docker image will contain all the necessary python requirements to run the app/script.


## Getting Started

### Clone this repo to your workstation / Create AWS Account
Repository contents:
- `envs` : contains sample environment file to pass credentials during `docker run` (this is an option; you can also just set env variables on the CLI.  Both methods are detailed below.)
- `src/copy-s3bucket.py` - python script that does the heavy lifting of copying form s3 bucket to s3 bucket
- `src/requirements.txt` - third party pre-reqs (only needed if testing outside the docker image.  Otherwise this is included in the image) 
- `Dockerfile` : dockerfile for creating the docker image to run the python 
- `Makefile` : simple makefile for easy docker build/run/cleanup etc
- `.git-secrets-init` : simple custom dotfile autogened when applying [git-secrets](https://github.com/awslabs/git-secrets) to the repo during repo initialization

This assumes you already have an AWS account. If not, you can sign up for the [free tier](https://aws.amazon.com/free/?nc2=h_ql_pr) to work with this code.  For an easy start, you can create an IAM user with "AdministratorAccess" or "AmazonS3FullAccess".  Make note of your `AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY`.  You will also want to note the region the buckets you are working with are located.

NOTE: A more secure setup would be to only add the permission policy needed (least privs).  For this project, you should probably only need : (s3:Get*, s3:List*, s3:Put*).



### Locate/Create Two S3 Buckets (Source, Destination)
Determine an existing S3 bucket with data to use as the source bucket and create a new destination bucket.  Optionally, you may want to just create two new S3 buckets (source,destination) for use.  You can use the AWS CLI or the console to accomplish this.  Once this is completed, push some files/directories/data etc to the source bucket.



## Usage

###  1. Setup AWS Credentials
Setup the code to use the AWS credentials you have previously created by doing one of the following.  We will use these credentials to pass into the docker container at runtime via environment variables or an environment file (ontaining env variables).


#### Choose one of the two options below:

If you wish to use environment variables to set the AWS credentials, please set them on the CLI (on your host that will run the docker container) as below.  Keep this session open for use in later steps:

```
export AWS_ACCESS_KEY_ID=youraccesskey
export AWS_SECRET_ACCESS_KEY=yousecretkey
export AWS_DEFAULT_REGION=us-west-2
```

OR instead if you wish to use an environment file for the credential:  Create a file in `envs/` with a name besides 'example' - a good name might be your current username.  Copy the contents of the `example` file to this new file and populate with your AWS credentials and region.  Note the name of this file as we will use it in the *1. Run Docker Container* step below as a argument to the Makefile in order to run the container.


The following commands will create a new env credentials file that you can modify:
```
cp envs/example envs/$(whoami)
cat envs/example | tee envs/$(whoami)
```

NOTE: DO NOT USE THE EXAMPLE FILE!!  CREATE YOUR OWN CREDENTIALS FILE AS A COPY!


###  2. Build Docker Image
Build the docker image we will use for this project.  In order to do so we will use the included Makefile to make the process a bit easier.  



First you will probably want to open the Makefile and edit the first two variables to suit your needs.  This is the name (NAME) that will be assigned to the container and the image name (IMAGE) to use when building the docker image.

```
NAME="s3-bucketcopy"
IMAGE="brianprovenzano/s3-bucketcopy"
```



Now use the command below to build the docker image.  We will use the `version` var to set a tag on the image for this build.
```
make build version=1.0

```


###  3. Run Docker Container
Now we are ready to run the bucket copy container.


Run the docker image.  Where `version` is the image:tag of the docker image created in step 2, `sourcebucket` is s3 source bucket, `destinationbucket` is the s3 copy destination and `threshold` is the size threshold (in bytes) for the keys/objects to copy (i.e. any file below this threshold size will NOT be copied)

```
make run version=1.0 sourcebucket=yoursourcebucket destinationbucket=yourdestinationbucketnamename threshold=500
```


OR if using env file: `version` is the image:tag of the docker image created in step 2, `env` is the name of the AWS credentials environment file you (optionally) created, `sourcebucket` is s3 source bucket, `destinationbucket` is the s3 copy destination and `threshold` is the size threshold (in bytes) for the keys/objects to copy.

```
make run-envfile version=1.0 env=yourenvfilename sourcebucket=yoursourcebucketname destinationbucket=yourdestinationbucketnae threshold=500
```

NOTE: Docker container is set to run attahed and auto remove itself on termination.  However, you can change this in the Makefile.



## Cleanup
If you wish to cleanup the docker images used in this project when you are finished, run the following:


List all the images on your machine/host and note the image(s) created: one with the name you specified earlier in the Makefile in step 2 and the alpine python image this container is based on.  Should only be these 2 images if you executed one build.
```
> docker image ls
REPOSITORY                      TAG                 IMAGE ID            CREATED             SIZE
brianprovenzano/s3-bucketcopy   1.0                 0e2e7b32b440        4 seconds ago       167MB
python                          3.7.3-alpine3.9     a93594ce93e7        4 days ago          90.9MB
rundeck/rundeck                 3.0.16              c479ea64a6bd        5 weeks ago         496MB
warpigg/nodejs                  latest              b117faecff45        7 weeks ago         895MB
node                            8                   4f01e5319662        7 weeks ago         893MB
ubuntu                          latest              47b19964fb50        7 weeks ago         88.1MB
node                            alpine              ebbf98230a82        8 weeks ago         73.7MB
chef/chefdk                     latest              52624c7d7030        2 months ago        830MB
alpine                          latest              caf27325b298        2 months ago        5.53MB

```


Delete the images.  In the example above it would be as follows, using the imageID for the first two images:

```
> docker image rm 0e2e7b32b440
> docker image rm a93594ce93e7
```
