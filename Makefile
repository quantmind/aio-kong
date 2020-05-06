.PHONY: help

help:
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'

black: 		## run black and fix files
	@./dev/run-black.sh

clean:		## remove python cache files
	find . -name '__pycache__' | xargs rm -rf
	find . -name '*.pyc' -delete
	rm -rf build
	rm -rf dist
	rm -rf aio_kong.egg-info
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .coverage

version:	## display software version
	@python3 -c "import kong; print(kong.__version__)"

services:	## Starts services
	@docker-compose -f ./dev/docker-compose.yml up --remove-orphans

services-ci:	## Starts CI services
	@docker-compose -f ./dev/docker-compose.yml up --remove-orphans -d

py36:		## build python 3.6 image for testing
	docker build -f dev/Dockerfile --build-arg PY_VERSION=python:3.6.10 -t pykong36 .

py37:		## build python 3.7 image for testing
	docker build -f dev/Dockerfile --build-arg PY_VERSION=python:3.7.7 -t pykong37 .

py38:		## build python 3.8 image for testing
	docker build -f dev/Dockerfile --build-arg PY_VERSION=python:3.8.2 -t pykong38 .

test-py36:	## test with python 3.6
	@docker run --rm --network=host pykong36 pytest

test-py37:	## test with python 3.7
	@docker run --rm --network=host pykong37 pytest

test-py38:	## test with python 3.8 with coverage
	@docker run --rm --network=host \
		-v $(PWD)/build:/workspace/build \
		pykong38 \
		pytest --cov --cov-report xml

test-black: 	## run black check in CI
	@docker run --rm \
		-v $(PWD)/build:/workspace/build \
		pykong38 \
		./dev/run-black.sh --check

test-flake8: 	## run flake8 in CI
	@docker run --rm \
		-v $(PWD)/build:/workspace/build \
		pykong38 \
		flake8
