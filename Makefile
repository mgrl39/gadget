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
	# Commands to build the project

.PHONY: test
test:
	# Commands to run tests
