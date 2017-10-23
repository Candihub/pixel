# Assets
CSS_DIR           = static/css
SASS_INCLUDE_PATH = node_modules/foundation-sites/scss/

# Node
YARN_RUN = yarn
NODEMON  = $(YARN_RUN) nodemon
POSTCSS  = $(YARN_RUN) postcss
SASS     = $(YARN_RUN) node-sass

# Docker
COMPOSE              = docker-compose -f docker-compose.yml -p pixel-dev
COMPOSE_RUN          = $(COMPOSE) run --rm
COMPOSE_RUN_WEB      = $(COMPOSE_RUN) web
MANAGE               = $(COMPOSE_RUN_WEB) ./manage.py
COMPOSE_TEST         = docker-compose -f docker-compose.test.yml -p pixel-test
COMPOSE_TEST_RUN     = $(COMPOSE_TEST) run --rm
COMPOSE_TEST_RUN_WEB = $(COMPOSE_TEST_RUN) web

default: help

bootstrap: ## install development dependencies
	@if [ -z "$$CI" ] || [ -n "$$CI_BUILD_BACKEND" ]; then $(COMPOSE) build web; ${MAKE} migrate-db; fi
	@if [ -z "$$CI" ] || [ -n "$$CI_BUILD_FRONTEND" ]; then yarn install -D; ${MAKE} build-css; fi
.PHONY: bootstrap

watch-css: ## continuously build CSS
	@$(NODEMON) -e scss -x 'make build-css'
.PHONY: watch-css

build-css: ## build CSS with Sass, Autoprefixer, etc.
	@$(SASS) --output-style compressed --include-path $(SASS_INCLUDE_PATH) assets/scss/main.scss $(CSS_DIR)/main.css
	@$(POSTCSS) $(CSS_DIR)/*.css -r --use autoprefixer
.PHONY: build-css

migrate-db:  ## perform database migrations
	@$(MANAGE) migrate
.PHONY: migrate-db

run-server: ## start the development server
	@$(COMPOSE) up
.PHONY: run-server

stop-server: ## stop the development server
	@$(COMPOSE) stop
.PHONY: stop-server

dev: ; ${MAKE} -j2 watch-css run-server ## start the dev environment
.PHONY: dev

test:  ## run the test suite
	@$(COMPOSE_TEST_RUN_WEB) pytest
.PHONY: test

test-ci:  ## run the test suite (CI context)
	pipenv run pytest
.PHONY: test-ci

coverage-ci:  ## publish coverage statistics (CI context)
	pipenv run coveralls
.PHONY: coverage-ci

lint:  ## lint the code
	@$(COMPOSE_RUN_WEB) flake8
.PHONY: lint

lint-ci:  ## lint the code (CI context)
	pipenv run flake8
.PHONY: lint-ci

install-ci:  ## install development dependencies (CI context)
	pipenv install -d
.PHONY: install-ci

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
.PHONY: help
