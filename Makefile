PORT := /dev/cu.SLAB_USBtoUART
RPI_IP := 192.168.0.108
MICROPYTHON_BIN := esp8266-20191220-v1.12.bin

.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: erase
erase: ## Erase flash
	esptool.py --port $(PORT) erase_flash

.PHONE: flash-python
flash-python: erase ## Flash micropython
	esptool.py --port $(PORT) --baud 460800 write_flash --flash_size=detect 0 $(MICROPYTHON_BIN)

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

.PHONY: deploy-app
deploy-app: ## Deploy application to rpi
	ssh pi@$(RPI_IP) 'sudo -u laser-remote bash -c "cd /home/laser-remote/app && git pull && source venv/bin/activate && pip install -r deploy_requirements.txt && python manage.py collectstatic --no-input" && sudo systemctl reload laser-remote'

.PHONY: local-remote
local-remote: ## Local environment with mosquitto client
	docker-compose run client
