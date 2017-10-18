# Assets
CSS_DIR           = static/css
SASS_INCLUDE_PATH = node_modules/foundation-sites/scss/

# Node
YARN_RUN = yarn
NODEMON  = $(YARN_RUN) nodemon
POSTCSS  = $(YARN_RUN) postcss
SASS     = $(YARN_RUN) node-sass

# Docker
COMPOSE         = docker-compose
COMPOSE_RUN     = $(COMPOSE) run --rm
COMPOSE_RUN_WEB = $(COMPOSE_RUN) web
MANAGE          = $(COMPOSE_RUN_WEB) ./manage.py

default: help

bootstrap: ## install development dependencies
	@if [ -z "$$CI" ] || [ -n "$$CI_BUILD_BACKEND" ]; then $(COMPOSE) build web; fi
	@if [ -z "$$CI" ] || [ -n "$$CI_BUILD_FRONTEND" ]; then yarn install -D; fi
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

dev: ; ${MAKE} -j2 watch-css run-server ## start the dev environment
.PHONY: dev

test:  ## run the test suite
	@$(COMPOSE_RUN_WEB) pytest
.PHONY: test

coverage:  ## publish coverage statistics
	@$(COMPOSE_RUN_WEB) coveralls
.PHONY: coverage

lint:  ## lint the code
	@$(COMPOSE_RUN_WEB) flake8
.PHONY: lint

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
.PHONY: help
