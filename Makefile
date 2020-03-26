PORT := /dev/cu.SLAB_USBtoUART

.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: repl
repl: ## Get MicroPython REPL
	picocom $(PORT) -b115200

.PHONY: sync-device
sync-device: ## Sync device code to microcontroller
	ampy --port $(PORT) put device/config.py
	ampy --port $(PORT) put common/boot.py
	ampy --port $(PORT) put device/main.py

.PHONY: sync-remote
sync-remote: ## Sync remote code to microcontroller
	ampy --port $(PORT) put remote/config.py
	ampy --port $(PORT) put common/boot.py
	ampy --port $(PORT) put remote/main.py

.PHONY: local-remote
local-remote: ## Local environment with mosquitto client
	docker-compose run client
