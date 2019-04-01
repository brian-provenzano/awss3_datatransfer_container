NAME="s3-bucketcopy"
IMAGE="brianprovenzano/s3-bucketcopy"

build:
	@docker build -t $(IMAGE):$(version) .
#set to auto remove the container after execution; not detaching...
run:
	@docker run --rm -e AWS_ACCESS_KEY_ID=$(AWS_ACCESS_KEY_ID) -e AWS_SECRET_ACCESS_KEY=$(AWS_SECRET_ACCESS_KEY) -e AWS_DEFAULT_REGION=$(AWS_DEFAULT_REGION) --name=$(NAME) brianprovenzano/s3-bucketcopy:$(version) $(sourcebucket) $(destinationbucket) $(threshold)
run-envfile:
	@docker run --rm --env-file envs/$(env) --name=$(NAME) brianprovenzano/s3-bucketcopy:$(version) $(sourcebucket) $(destinationbucket) $(threshold)
start:
	@docker container start $(NAME)
stop:
	@docker container stop $(NAME)
show:
	@docker container ls
logs: 
	@docker logs $(NAME)
cli:
	@docker container exec -it -u root $(NAME) /bin/bash
clean:	stop
	@docker container rm $(NAME)