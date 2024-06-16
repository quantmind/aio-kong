.PHONY: help

help:
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'


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
	@poetry run ./dev/lint-code fix


lint-check: 		## run black check in CI
	@poetry run ./dev/lint-code


outdated:		## Show outdated packages
	poetry show -o -a


version:		## display software version
	@poetry run python -c "import kong; print(kong.__version__)"


services:		## Starts services
	@docker-compose -f ./dev/docker-compose.yml up --remove-orphans


services-ci:		## Starts CI services
	@docker-compose -f ./dev/docker-compose.yml up --remove-orphans -d


test:			## run tests
	@poetry run pytest -x -vvv --cov --cov-report xml --cov-report html


test-codecov:		## upload code coverage
	@poetry run codecov --token $(CODECOV_TOKEN) --file ./build/coverage.xml


test-version:		## check version compatibility
	@./dev/test-version


publish:		## release to pypi and github tag
	@poetry publish --build -u __token__ -p $(PYPI_TOKEN)
