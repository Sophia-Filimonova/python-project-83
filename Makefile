install:
	poetry install

lint:
	poetry run flake8 page_analyzer

test:
	poetry run pytest -vv

test-coverage:
	poetry run pytest --cov=gendiff tests/ --cov-report xml 

selfcheck:
	poetry check

check: selfcheck lint test

gendiff:
	poetry run gendiff

build: check
	poetry build

publish:
	poetry publish --dry-run

package-install:
	python3 -m pip install --user dist/*.whl

dev:
	poetry run flask --app page_analyzer:app run

PORT ?= 8000
start:
	poetry run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app

.PHONY: install test lint selfcheck check page_analyzer build