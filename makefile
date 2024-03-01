.ONESHELL:
.SILENT:
.EXPORT_ALL_VARIABLES:
.PHONY: default

default: settings

###############################################################################
# Targets
###############################################################################
app_name := llmdoc
VERSION := $(shell awk -F'[ ="]+' '$$1 == "version" { print $$2 }' pyproject.toml)
docker_registry := ghcr.io/kborovik
docker_image ?= ${docker_registry}/${app_name}

ELASTIC_VERSION := 8.12.0
ELASTIC_USER ?= elastic
ELASTIC_PASSWORD ?= $(shell grep -is ELASTIC_PASSWORD .env | cut -d "=" -f 2)

OLLAMA_VERSION := 0.1.26

PAUSE ?= 0

test_query ?= 'Who is Count Von Kramm?'

###############################################################################
# Files
###############################################################################
ca_crt := certs/ca.crt

${ca_crt}:
	mkdir -p certs
	docker cp elastic-1:/usr/share/elasticsearch/config/certs/ca.crt $@

###############################################################################
# Targets
###############################################################################
settings:
	echo "#######################################################################"
	echo "# VERSION=${VERSION}"
	echo "# ELASTIC_USER=${ELASTIC_USER}"
	echo "# ELASTIC_PASSWORD=${ELASTIC_PASSWORD}"
	echo "# docker_image=${docker_registry}/${app_name}:${VERSION}"
	echo "# test_query='${test_query}'"
	echo "#######################################################################"

init: .elastic-init .env start ${ca_crt}

build: poetry-build docker-build

poetry-build:
	$(call header,Build Python Wheel)
	poetry build --format=wheel
	poetry export --format requirements.txt --output dist/requirements.txt --without-hashes

docker-build:
	$(call header,Build Docker Image)
	docker buildx build \
	--tag="${docker_image}:${VERSION}" \
	--tag="${docker_image}:latest" \
	--build-arg="VERSION=${VERSION}" \
	--file=Dockerfile dist/

docker-auth:
	$(call header,Docker Auth)
	GITHUB_TOKEN=$$(pass github/token/kborovik)
	echo $${GITHUB_TOKEN} | docker login ghcr.io -u kborovik --password-stdin

docker-push: docker-auth
	$(call header,Push Docker Image)
	docker push ${docker_image}:${VERSION}
	docker push ${docker_image}:latest

install: build
	$(call header,Install PIPX ${app_name})
	pipx install --force dist/${app_name}-${VERSION}-py3-none-any.whl

update:
	$(call header,Upgrade ${app_name})
	poetry lock
	poetry install

version:
	poetry version patch

commit: version
	version=$$(awk -F'[ ="]+' '$$1 == "version" { print $$2 }' pyproject.toml)
	git add --all
	git commit --message="version $${version}"

release: commit build docker-push
	$(call header,Create GitHub Release)
	version=$$(awk -F'[ ="]+' '$$1 == "version" { print $$2 }' pyproject.toml)
	git push --all
	gh release create $${version} dist/${app_name}-$${version}-py3-none-any.whl --title "Release $${version}" --notes "docker pull ${docker_image}:$${version}"
	git pull --all

clean: stop
	$(call header,Remove Python files)
	rm -rf **/__pycache__ **/**/__pycache__ dist ${ca_crt} .elastic-init
	$(call header,Remove Docker volumes)
	docker volume rm elastic || true
	docker volume rm kibana || true
	docker volume rm certs || true

start: build 
	$(call header,Start Docker Compose)
	docker compose up --detach --remove-orphans --wait

status:
	$(call header,Status Docker Compose)
	docker container ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}"
	echo

stop:
	$(call header,Stop Docker Compose)
	docker compose down --remove-orphans

run:
	$(call header,Run LLMDoc API)
	docker container stop llmdoc-1
	poetry run uvicorn llmdoc.api_v1:app --interface=wsgi --host=0.0.0.0 --no-access-log --reload --reload-dir=llmdoc

python-env-activate:
	echo "source $$(poetry env info --path)/bin/activate"

.env:
	echo "ELASTIC_PASSWORD=MyBigPass45" > $@

.elastic-init:
	set -e
	$(call header,Create Elastic and Kibana volumes)
	docker volume create elastic
	docker volume create kibana
	docker volume create certs
	docker volume create ollama
	$(call header,Create Elastic SSL certs)
	docker container run --name=elastic-init --user=root --tty --interactive --rm --volume=certs:/usr/share/elasticsearch/config/certs \
	docker.elastic.co/elasticsearch/elasticsearch:${ELASTIC_VERSION} \
	/bin/bash -c "elasticsearch-certutil ca --pem --pass=elastic-1 --out config/certs/ca.zip && unzip -j config/certs/ca.zip -d config/certs && \
	elasticsearch-certutil cert --pem --ip=127.0.0.1 --dns='elastic-1,localhost' --ca-cert=config/certs/ca.crt --ca-key=config/certs/ca.key --ca-pass=elastic-1 --pass=elastic-1 --out config/certs/instance.zip && \
	unzip -j config/certs/instance.zip -d config/certs && rm config/certs/*.zip && openssl rsa -passin pass:elastic-1 -in config/certs/ca.key -out config/certs/ca.key && \
	openssl rsa -passin pass:elastic-1 -in config/certs/instance.key -out config/certs/instance.key && chown -R 1000 config/certs"
	touch $@

index:
	set -e
	$(call header,Delete Elastic Index)
	poetry run llmdoc storage --delete
	$(call header,Add Document to Elastic)
	poetry run llmdoc index --file tests/sherlock-holmes.txt

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

shell-llmdoc:
	docker container exec --tty --interactive llmdoc-1 /bin/bash

test: start test-index test-search test-app

ollama-model:
	$(call header,Pull Ollama Model)
	poetry run llmdoc model

test-index: ollama-model
	$(call header,Test Indexing)
	set -e
	poetry run llmdoc storage --delete
	poetry run llmdoc index --file tests/test.txt

test-search: ollama-model
	$(call header,Test Base LLM: ${test_query})
	poetry run llmdoc generate --prompt ${test_query}
	$(call header,Test CLI Search: ${test_query})
	poetry run llmdoc search --query ${test_query}

test-app:
	$(call header,Test API Search: ${test_query})
	http POST http://localhost:8000/search query=${test_query}

###############################################################################
# Demo
###############################################################################
demo-init:
	asciinema rec -t "llmdoc make init" -c "PAUSE=3 make init status"

demo-test:
	asciinema rec -t "llmdoc make test" -c "PAUSE=3 make test"

demo-search:
	asciinema rec -t "llmdoc search debug" -c "poetry run llmdoc search --query ${test_query} --debug --search-size 2"

demo-index:
	asciinema rec -t "llmdoc index debug" -c "poetry run  llmdoc index --file tests/test.txt --debug"

###############################################################################
# Functions
###############################################################################
define header
echo
echo "########################################################################"
echo "# $(1)"
echo "########################################################################"
sleep ${PAUSE}
endef

###############################################################################
# Errors
###############################################################################
ifeq ($(shell command -v docker),)
$(error ==> Install Docker https://docs.docker.com/ <==)
endif

ifeq ($(shell command -v poetry),)
$(error ==> Install Python `poetry`  https://github.com/python-poetry/poetry <==)
endif
