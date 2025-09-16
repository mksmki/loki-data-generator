.PHONY: help
VERSION:=$(shell grep VERSION ./app/loki_data_generator/setup.py | head -n1 | cut -d"'" -f2)

help:
	@echo "Please use 'make <target>' where <target> is one of"
	@echo "  clean                       remove *.pyc files, __pycache__ and *.egg-info directories"
	@echo "  test                        execute tests"
	@echo "  build                       build the docker image"
	@echo "  push                        push the docker image"
	@echo "Check the Makefile to know exactly what each target is doing."

clean:
	@echo "Deleting '*.pyc', '__pycache__' and '*.egg-info'..."
	find . -name '*.pyc' -delete
	find . -name '__pycache__' -type d | xargs rm -fr
	find . -name '*.egg-info' -type d | xargs rm -fr
	rm -fr dist build

docker-build:
	@docker build \
		-t mksmki/loki-data-generator:$(VERSION) .
	@docker tag mksmki/loki-data-generator:$(VERSION) \
		mksmki/loki-data-generator:latest

docker-push:
	# @docker tag mksmki/loki-data-generator:latest mksmki/loki-data-generator:$(VERSION)
	@docker push mksmki/loki-data-generator:latest
	@docker push mksmki/loki-data-generator:$(VERSION)

run:
	docker run --rm -ti --name ldg -v `pwd`/config.yaml:/app/config.yaml \
		-e LDG_LOG_LEVEL=DEBUG -p 127.0.0.1:9000:9000 \
		mksmki/loki-data-generator:latest

all: clean docker-build docker-push
