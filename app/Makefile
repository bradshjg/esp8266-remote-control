.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: local
local: ## Run local development environment
	docker-compose -f docker-compose.dev.yml up

.PHONY: test
test: ## Run test suite
	docker-compose -f docker-compose.dev.yml -f docker-compose.test.yml run app
