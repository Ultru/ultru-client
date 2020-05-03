# Ultru Makefile

assemble:
	rm -rf dist/
	python setup.py sdist bdist_wheel

clean:
	find . -name '*.pyc' -exec rm --force {} \;
	find . -name '*.pyo' -exec rm --force {} \;
	find . -name '*~' -exec rm --force  {} \;

lint:
	pylint -E src/

.PHONY: tests
tests:
	pytest --cov=ultru_client tests/

upload: assemble
	twine upload dist/*

