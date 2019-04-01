NAME="s3-bucketcopy"
IMAGE="brianprovenzano/s3-bucketcopy"

build:
	@docker build -t $(IMAGE):$(version) .
#set to auto remove the container after execution
run:
	@docker run --rm -e AWS_ACCESS_KEY_ID=$(accesskey) -e AWS_SECRET_ACCESS_KEY=$(secretkey) -e AWS_DEFAULT_REGION=$(region) --name=$(NAME) -d brianprovenzano/s3-bucketcopy:$(version)
run-envfile:
	@docker run --rm --env-file envs/$(ENV) --name=$(NAME) -d brianprovenzano/s3-bucketcopy:$(version)
run-logs: run logs
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