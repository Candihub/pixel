default: help

bootstrap: ## install the project dependencies
	pipenv install -d
	yarn install -D
.PHONY: bootstrap

migrate-db:  ## perform database migrations
	pipenv run python manage.py migrate
.PHONY: migrate-db

dev: ## start the dev environment
	pipenv run python manage.py runserver
.PHONY: dev

test:  ## run the test suite
	pipenv run pytest
.PHONY: test

coverage:  ## publish coverage statistics
	pipenv run coveralls
.PHONY: coverage

lint:  ## lint the code
	pipenv run flake8
.PHONY: lint

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
.PHONY: help
