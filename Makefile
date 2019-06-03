.PHONY: clean-pyc clean-build clean docs lint test doctest version gunicorn

# Setup
VERSION=1.1.0
SOURCE_PATH=./rpi433rc
TEST_PATH=./tests

# Environment overrides
VERSION_PART?=patch

help:
		@echo "    clean"
		@echo "        Remove python and release artifacts."
		@echo "    setup"
		@echo "        Installs dependencies into the environment"
		@echo "    lint"
		@echo "        Check style with flake8."
		@echo "    test"
		@echo "        Run py.test"
		@echo "    doctest"
		@echo "        Run doctest"
		@echo "    version"
		@echo "        Prints out the current version"

clean-pyc:
		find . -name '*.pyc' -delete
		find . -name '*.pyo' -delete
		# find . -name '*~' -exec rm --force  {} +

clean-build:
		rm -rf build/
		rm -rf dist/
		rm -rf *.egg-info
		rm -rf .pytest_cache

clean: clean-pyc clean-build

setup:
		pip install -r requirements.txt
		pip install -r requirements-dev.txt

lint:
		flake8 --exclude=.tox --max-line-length 120 --ignore=E722 --ignore=E402 $(SOURCE_PATH)
		pylint $(SOURCE_PATH)

test:
		pytest --verbose --color=yes \
			--doctest-modules \
			--cov=$(SOURCE_PATH) --cov-report html --cov-report term $(TEST_PATH) \
			$(SOURCE_PATH)

doctest:
		pytest --verbose --color=yes --doctest-modules $(SOURCE_PATH)

version:
		@echo $(VERSION)

next-version: lint test
		$(eval NEXT_VERSION := $(shell bumpversion --dry-run --allow-dirty --list $(VERSION_PART) | grep new_version | sed s,"^.*=",,))
		@echo Next version is $(NEXT_VERSION)
		bumpversion $(VERSION_PART)
		@echo "Review your version changes first"
		@echo "Accept your version: \`make accept-version\`"
		@echo "Revoke your version: \`make revoke-version\`"

accept-version:
		git push && git push --tags

revoke-version:
		git tag -d `git describe --tags --abbrev=0`    # delete the tag
		git reset --hard HEAD~1                        # rollback the commit

server:
		OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES \
			PYTHONPATH=`pwd` \
			python `pwd`/rpi433rc/runner.py

mqtt:
		docker run --rm -d -p 1883:1883 eclipse-mosquitto:1.6

pin:
		pip-compile --output-file requirements.txt requirements.in
