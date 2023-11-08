.PHONY: install test develop lint lint-commit update-dependencies

lint-commit:
	poetry run pre-commit run
install:
	pip install -r requirements.txt
test:
	poetry run pytest .
develop:
	poetry install
	poetry run pre-commit install
lint:
	poetry run pre-commit run --all-files
update-dependencies:
	poetry export -f requirements.txt -o requirements.txt

