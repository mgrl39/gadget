GREEN=\033[0;32m
RED=\033[0;31m
BLUE=\033[0;34m
END=\033[0m

.DEFAULT_GOAL := help

all: 

help:

pull:
	git fetch && git pull origin $(shell git branch --show-current)

.PHONY: all help pull
