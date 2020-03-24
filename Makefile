PORT := /dev/cu.SLAB_USBtoUART

.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: sync
sync: ## Sync files to microcontroller
	ampy --port $(PORT) put main.py
	ampy --port $(PORT) put config.py
	ampy --port $(PORT) put main.py

.PHONY: local
local: ## Local environment with mosquitto client
	docker-compose run client
