.PHONY: help

help:
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'

black: 			## run black and fix files
	@./dev/run-black.sh

bundle3.6:		## build python 3.6 bundle
	@python setup.py bdist_wheel --python-tag py36

bundle3.7:		## build python 3.7 bundle
	@python setup.py bdist_wheel --python-tag py37

bundle3.8:		## build python 3.8 bundle
	@python setup.py bdist_wheel --python-tag py38

bundle3.9:		## build python 3.9 bundle
	@python setup.py sdist bdist_wheel --python-tag py39

clean:			## remove python cache files
	find . -name '__pycache__' | xargs rm -rf
	find . -name '*.pyc' -delete
	rm -rf build
	rm -rf dist
	rm -rf aio_kong.egg-info
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .coverage

install: 		## install packages in virtualenv
	@./dev/install

lint: 			## run linters
	isort .
	./dev/run-black
	flake8


lint-check: 		## run black check in CI
	isort . --check
	./dev/run-black --check
	flake8


version:		## display software version
	@python3 -c "import kong; print(kong.__version__)"

services:		## Starts services
	@docker-compose -f ./dev/docker-compose.yml up --remove-orphans

services-ci:		## Starts CI services
	@docker-compose -f ./dev/docker-compose.yml up --remove-orphans -d

test:			## run tests
	@pytest -x --cov --cov-report xml

test-codecov:		## upload code coverage
	@codecov --token $(CODECOV_TOKEN) --file ./build/coverage.xml

test-version:		## validate version with pypi
	@agilekit git validate

release-github:		## new tag in github
	@agilekit git release --yes

release-pypi:		## release to pypi and github tag
	@twine upload dist/* --username lsbardel --password $(PYPI_PASSWORD)

github-tag:		## new tag in github
	@GITHUB_TOKEN=$(QMBOT_TOKEN) agilekit git release --yes

pypi:			## release to pypi and github tag
	@twine upload dist/* --username lsbardel --password $(PYPI_PASSWORD)

release:		## release to pypi and github tag
	make pypi
	make github-tag
