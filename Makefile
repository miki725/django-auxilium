help:  ## show help
	@grep -E '^[a-zA-Z_\-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		cut -d':' -f1- | \
		sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## install all dependencies
	pip install -U -r requirements-dev.txt

install-quite:  ## install all dependencies quietly piping output to /dev/null
	pip install -r requirements-dev.txt > /dev/null

clean: clean-build clean-pyc clean-test  ## clean everything except tox

clean-build:  ## clean build and distribution artifacts
	@rm -rf build/
	@rm -rf dist/
	@rm -rf *.egg-info

clean-pyc:  ## clean pyc files
	-@find . -path ./misc -prune -o -name '*.pyc' -follow -print0 | xargs -0 rm -f
	-@find . -path ./misc -prune -o -name '*.pyo' -follow -print0 | xargs -0 rm -f
	-@find . -path ./misc -prune -o -name '__pycache__' -type d -follow -print0 | xargs -0 rm -rf

clean-test:  ## clean test artifacts like converage
	rm -rf .coverage coverage*
	rm -rf htmlcov/

clean-all: clean  ## clean everything including tox
	rm -rf .tox/

lint:  ## lint whole library
	flake8 .
	importanize --ci django_auxilium tests test_project

test:  ## run all tests
	py.test -sv --doctest-modules --cov=django_auxilium --cov-report=term-missing django_auxilium/ tests/

test-all:  ## run all tests with tox with different python/django versions
	tox

check: clean lint test  ## check library which runs lint and tests

release: clean  ## push release to pypi
	python setup.py sdist bdist_wheel upload

dist: clean  ## create distribution of the library
	python setup.py sdist bdist_wheel
	ls -l dist
