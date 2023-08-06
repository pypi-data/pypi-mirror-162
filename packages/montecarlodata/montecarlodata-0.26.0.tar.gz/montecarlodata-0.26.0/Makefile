.PHONY: default clean install pip-install test install-with-tests distribute
ENVIRONMENT_NAME=venv

default:
	@echo "Read the readme"

clean:
	rm -rf $(ENVIRONMENT_NAME) build dist montecarlodata.egg-info .coverage nosetests.xml

install: clean
	virtualenv $(ENVIRONMENT_NAME); \
	. $(ENVIRONMENT_NAME)/bin/activate; \
	pip install -r requirements-dev.txt; \
	$(MAKE) pip-install; \
	montecarlo --version

pip-install:
	pip install --editable .

test:
	@# Requires activating the virtualenv created in `install` if running locally
	export DEBUG=True; unset MCD_USER_ID_HEADER; coverage run -m pytest ./tests

install-with-tests: install
	. $(ENVIRONMENT_NAME)/bin/activate; $(MAKE) test

distribute: install
	. $(ENVIRONMENT_NAME)/bin/activate; \
	pip install -r requirements-ci.txt; \
	python setup.py sdist bdist_wheel; \
	twine check dist/*; \
	twine upload --non-interactive dist/*