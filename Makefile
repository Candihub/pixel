# assets
CSS_DIR           = static/css
FONTS_DIR         = static/fonts
FOUNDATION_PATH = node_modules/foundation-sites
FA_PATH = node_modules/font-awesome

# Node
YARN_RUN = yarn
NODEMON  = $(YARN_RUN) nodemon
POSTCSS  = $(YARN_RUN) postcss
SASS     = $(YARN_RUN) node-sass

# Docker
COMPOSE              = bin/compose
COMPOSE_RUN          = $(COMPOSE) run --rm
COMPOSE_RUN_WEB      = $(COMPOSE_RUN) web
MANAGE               = bin/manage
COMPOSE_TEST         = docker-compose -f docker-compose.test.yml -p pixel-test
COMPOSE_TEST_RUN     = $(COMPOSE_TEST) run --rm
COMPOSE_TEST_RUN_WEB = $(COMPOSE_TEST_RUN) web

# User
# For the `?=` operator, see: https://www.gnu.org/software/make/manual/make.html#Flavors
UID ?= $(shell id -u)
GID ?= $(shell id -g)

# node
#
# $YARN_VERSION environment variable is defined in node container, but hopefully
# not in user's environment. We use this environment variable definition to
# automatically switch yarn execution via docker-compose or from the container.
# This trick is required to run the 'watch-css' rule via docker-compose.
ifeq "$(YARN_VERSION)" ""
	YARN_RUN = $(COMPOSE_RUN_NODE) yarn
else
	YARN_RUN = yarn
endif
NODEMON  = $(YARN_RUN) nodemon
POSTCSS  = $(YARN_RUN) postcss
SASS     = $(YARN_RUN) node-sass

default: help

bootstrap: ## install development dependencies
	@if [ -z "$$CI" ] || [ -n "$$CI_BUILD_BACKEND" ]; then \
		$(COMPOSE) build --build-arg UID=$(UID) --build-arg GID=$(GID) web; \
		echo 'Waiting until database is up'; \
		sleep 20; \
		${MAKE} migrate-db; \
		$(MANAGE) loaddata apps/data/fixtures/initial_data.json; \
		$(MANAGE) loaddata apps/core/fixtures/initial_data.json; \
		$(MANAGE) make_development_fixtures; \
	fi
	@if [ -z "$$CI" ] || [ -n "$$CI_BUILD_FRONTEND" ]; then \
		$(YARN_RUN) install -D; \
		${MAKE} build-css; \
	fi
.PHONY: bootstrap

watch-css: ## continuously build CSS
	@$(NODEMON) -e scss -x 'make build-css'
.PHONY: watch-css

build-css: ## build CSS with Sass, Autoprefixer, etc.
	@mkdir -p static/fonts
	@cp -f $(FA_PATH)/fonts/* $(FONTS_DIR)/
	@$(SASS) --output-style compressed \
		--include-path $(FOUNDATION_PATH)/scss/ \
		--include-path $(FA_PATH)/scss/ \
		assets/scss/main.scss \
		$(CSS_DIR)/main.css
	@$(POSTCSS) $(CSS_DIR)/*.css -r --use autoprefixer
.PHONY: build-css

migrate-db:  ## perform database migrations
	@$(MANAGE) migrate
.PHONY: migrate-db

logs: ## get development logs
	@$(COMPOSE) logs -f
.PHONY: logs

run-server: ## start the development server
	@$(COMPOSE) up -d
.PHONY: run-server

stop-server: ## stop the development server
	@$(COMPOSE) stop
.PHONY: stop-server

restart-server: ## re-start the development server
	@$(COMPOSE) restart web
.PHONY: restart-server

dev: ; ${MAKE} -j2 watch-css run-server ## start the development environment
.PHONY: dev

down-test: ## cleanup docker test containers
	@$(COMPOSE_TEST) down
.PHONY: down-test

down-dev: ## cleanup docker development containers
	@$(COMPOSE) down
.PHONY: down-dev

down: ## cleanup docker development and test containers
	${MAKE} down-dev && ${MAKE} down-test
.PHONY: down

test:  ## run the test suite
	@$(COMPOSE_TEST_RUN) -v $(PWD):/app/pixel web pytest
.PHONY: test

test-ci:  ## run the test suite (CI context)
	@$(COMPOSE_TEST_RUN) \
		-e COVERALLS_REPO_TOKEN=$(COVERALLS_REPO_TOKEN) \
		-e CI=$(CI) \
		-e CIRCLECI=$(CIRCLECI) \
		-e CIRCLE_BRANCH=$(CIRCLE_BRANCH) \
		-e CIRCLE_BUILD_NUM=$(CIRCLE_BUILD_NUM) \
		-e CI_PULL_REQUEST=$(CI_PULL_REQUEST) \
		web \
		bin/ci --test-with-coverage
.PHONY: test-ci

coverage-ci:  ## publish coverage statistics (CI context)
	@$(COMPOSE_TEST_RUN_WEB) coveralls
.PHONY: coverage-ci

lint:  ## lint the code
	@$(COMPOSE_TEST_RUN_WEB) flake8
.PHONY: lint

rebuild: ## rebuild docker development and test containers
	${MAKE} rebuild-dev && ${MAKE} rebuild-test
.PHONY: rebuild

rebuild-dev: ## rebuild the development container
	@$(COMPOSE) build --build-arg UID=$(UID) --build-arg GID=$(GID) web
.PHONY: rebuild-dev

rebuild-test: ## rebuild the test container
	@$(COMPOSE_TEST) build --build-arg UID=$(UID) --build-arg GID=$(GID) web
.PHONY: rebuild-test

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
.PHONY: help
