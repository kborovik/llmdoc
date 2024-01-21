.ONESHELL:
.SILENT:
.EXPORT_ALL_VARIABLES:
.PHONY: default

default: settings

###############################################################################
# Targets
###############################################################################
app_name := llmdoc

ELASTIC_VERSION := 8.12.0
ELASTIC_PASSWORD ?= $(shell grep -i ELASTIC_PASSWORD .env | cut -d "=" -f 2)

ifeq ($(ELASTIC_PASSWORD),)
ELASTIC_PASSWORD := MyBigPass45
endif

LOGLEVEL ?= INFO

###############################################################################
# Files
###############################################################################
ca_crt := certs/ca.crt

${ca_crt}:
	mkdir -p certs
	docker cp elastic-1:/usr/share/elasticsearch/config/certs/ca.crt certs/ca.crt

###############################################################################
# Targets
###############################################################################
settings:
	echo "#######################################################################"
	echo "# LOGLEVEL=${LOGLEVEL}"
	echo "# ELASTIC_PASSWORD=${ELASTIC_PASSWORD}"
	echo "#######################################################################"

init: python-init .elastic-init

install:
	$(call header,Install PIPX ${app_name})
	pipx install .

upgrade:
	$(call header,Upgrade PIPX ${app_name})
	pipx upgrade ${app_name}

patch:
	poetry version patch

minor:
	poetry version minor

rebuild:
	set -e
	$(call header,Delete Elastic Index)
	poetry run llmdoc storage --delete
	$(call header,Add Document to Elastic)
	poetry run llmdoc index --file tests/happy-prince-by-oscar-wilde.txt

build: init
	poetry build

commit: patch
	version=$$(awk -F'[ ="]+' '$$1 == "version" { print $$2 }' pyproject.toml)
	git add --all
	git commit --message="revision $${version}"
	git push

clean: stop
	$(call header,Remove Python files)
	rm -rf **/__pycache__ **/**/__pycache__ dist ${ca_crt} .elastic-init poetry.lock
	pipx uninstall ${app_name} || true
	$(call header,Remove Docker volumes)
	docker volume rm elastic || true
	docker volume rm kibana || true
	docker volume rm certs || true

start:
	docker compose up --detach --remove-orphans --wait
	${MAKE} ${ca_crt}

status:
	docker container ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}"

stop:
	docker compose down --remove-orphans

python-init:
	$(call header,Initialize Python Environment)
	pip install -U pipx pip
	pipx install poetry
	poetry lock
	poetry install

python-env-activate:
	echo "source $$(poetry env info --path)/bin/activate"

.elastic-init:
	set -e
	$(call header,Create Elastic and Kibana volumes)
	docker volume create elastic
	docker volume create kibana
	docker volume create certs
	$(call header,Create Elastic SSL certs)
	docker container run --name=elastic-init --user=root --tty --interactive --rm --volume=certs:/usr/share/elasticsearch/config/certs \
	docker.elastic.co/elasticsearch/elasticsearch:${ELASTIC_VERSION} \
	/bin/bash -c "elasticsearch-certutil ca --pem --pass=elastic-1 --out config/certs/ca.zip && unzip -j config/certs/ca.zip -d config/certs && \
	elasticsearch-certutil cert --pem --ip=127.0.0.1 --dns='elastic-1,localhost' --ca-cert=config/certs/ca.crt --ca-key=config/certs/ca.key --ca-pass=elastic-1 --pass=elastic-1 --out config/certs/instance.zip && \
	unzip -j config/certs/instance.zip -d config/certs && rm config/certs/*.zip && openssl rsa -passin pass:elastic-1 -in config/certs/ca.key -out config/certs/ca.key && \
	openssl rsa -passin pass:elastic-1 -in config/certs/instance.key -out config/certs/instance.key && chown -R 1000 config/certs"
	touch $@

shell-elastic-init:
	$(call header,Init Elastic and Kibana)
	docker container run \
	--name=elastic-init \
	--user=root \
	--tty --interactive --rm \
	--volume=certs:/usr/share/elasticsearch/config/certs/ \
	docker.elastic.co/elasticsearch/elasticsearch:${ELASTIC_VERSION} /bin/bash

shell-ollama:
	docker container exec --tty --interactive ollama-1 /bin/bash

shell-elastic:
	docker container exec --tty --interactive elastic-1 /bin/bash

ollama-model:
	$(call header,Update Ollama Custom model)
	ollama create mistral -f models/search-assistant.mistral

test: ollama-model
	set -e
	$(call header,Test document index and search)
	export elastic_index_name=llmdoc-test
	export search_score=0.7
	poetry run llmdoc storage --delete
	poetry run llmdoc index --file tests/test-text.txt --debug
	sleep 2
	poetry run llmdoc search --query "what protestors demanded?" --debug

###############################################################################
# Functions
###############################################################################
define header
echo
echo "########################################################################"
echo "# $(1)"
echo "########################################################################"
endef

###############################################################################
# Errors
###############################################################################
ifeq ($(shell command -v docker),)
$(error ==> Install Docker <==)
endif

ifeq ($(shell command -v pip),)
$(error ==> Install Python PIP <==)
endif
