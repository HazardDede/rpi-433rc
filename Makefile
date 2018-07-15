.PHONY: clean-pyc clean-build

SOURCE_PATH=./rpi433rc
TEST_PATH=./tests

help:
		@echo "    clean-pyc"
		@echo "        Remove python artifacts."
		@echo "    clean-build"
		@echo "        Remove build artifacts."
		@echo "    lint"
		@echo "        Check style with flake8."
		@echo "    test"
		@echo "        Run py.test"

clean-pyc:
		find . -name '*.pyc' -delete
		find . -name '*.pyo' -delete
		# find . -name '*~' -exec rm --force  {} +

clean-build:
		rm --force --recursive build/
		rm --force --recursive dist/
		rm --force --recursive *.egg-info

clean: clean-pyc clean-build

pin:
		pip-compile --output-file requirements.txt requirements.in

lint:
		flake8 --exclude=.tox --max-line-length 120 --ignore=E402 $(SOURCE_PATH)

test:
		pytest --verbose --color=yes -s \
		    --doctest-modules \
		    --cov=$(SOURCE_PATH) --cov-report html --cov-report term \
		    $(TEST_PATH) $(SOURCE_PATH)

doctest:
		pytest --verbose --color=yes --doctest-modules $(SOURCE_PATH)

gunicorn:
		gunicorn --bind 0.0.0.0:5000 wsgi
