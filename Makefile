# Makefile

.PHONY: help
help:
	@grep -E '(^#|^[a-zA-Z_-]+:)' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?#"}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' | \
		awk 'NF > 1'

.PHONY: clean
clean: 
	rm -rf build

.PHONY: build
build:
	mkdir -p build

venv:
	source venv/bin/activate


.PHONY: install
install:
	@echo "Installing dependencies..."
	pip install -r requirements.txt

.PHONY: test
test:
	# TODO: command test
