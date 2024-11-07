BASE = $(shell pwd)

HELM_CHARTS ?= ska-tango-util ska-tango-base
HELM_CHARTS_TO_PUBLISH ?= $(HELM_CHARTS)

KUBE_NAMESPACE ?= ska-tango-charts#namespace to be used
RELEASE_NAME ?= test## release name of the chart
K8S_CHART = ska-tango-umbrella
ITANGO_VERSION ?= 9.5.0
CI_JOB_ID ?= local##pipeline job id
TEST_RUNNER ?= test-mk-runner-$(CI_JOB_ID)##name of the pod running the k8s_tests
TANGO_HOST ?= tango-databaseds:10000## TANGO_HOST connection to the Tango DS
SKA_TANGO_OPERATOR=true
K8S_CHARTS ?= ska-tango-util ska-tango-base ska-tango-umbrella## list of charts to be published on gitlab -- umbrella charts for testing purpose

CI_PROJECT_PATH_SLUG ?= ska-tango-charts
CI_ENVIRONMENT_SLUG ?= ska-tango-charts

RELEASE_VALUES_FILE ?= $(RELEASE_NAME).$(KUBE_NAMESPACE).values.yml
ifneq ($(K8S_VALUES_FILES),)
K8S_CHART_PARAMS ?= $(foreach f,$(K8S_VALUES_FILES),-f <(envsubst < $(f)))
ifneq ("$(wildcard $(RELEASE_VALUES_FILE))","")
$(info Infering environment from release information ...)
SKA_TANGO_OPERATOR := $(shell jq -r '.global.operator' $(RELEASE_VALUES_FILE))
TANGO_HOST := $(shell jq -r '.global.tango_host' $(RELEASE_VALUES_FILE))
$(info Setting SKA_TANGO_OPERATOR=$(SKA_TANGO_OPERATOR))
$(info Setting TANGO_HOST=$(TANGO_HOST))
endif
endif

PYTHON_VARS_BEFORE_PYTEST = SKA_TANGO_OPERATOR=$(SKA_TANGO_OPERATOR) TANGO_HOST=$(TANGO_HOST) PYTHONPATH=${PYTHONPATH}:/app:/app/tests KUBE_NAMESPACE=$(KUBE_NAMESPACE) HELM_RELEASE=$(RELEASE_NAME)

PYTHON_VARS_AFTER_PYTEST = --disable-pytest-warnings --timeout=300

RELEASE_SUPPORT := $(shell dirname $(abspath $(lastword $(MAKEFILE_LIST))))/.make-release-support

K8S_TEST_IMAGE_TO_TEST ?= artefact.skao.int/ska-tango-images-tango-itango:$(ITANGO_VERSION)

# include OCI Images support
include .make/oci.mk

# include k8s support
include .make/k8s.mk

# include Helm Chart support
include .make/helm.mk

# include raw support
include .make/raw.mk

# include core make support
include .make/base.mk

# include your own private variables for custom deployment configuration
-include PrivateRules.mak

# Colour bank https://stackoverflow.com/questions/4332478/read-the-current-text-color-in-a-xterm/4332530#4332530
RED=$(shell tput setaf 1)
GREEN=$(shell tput setaf 2)
YELLOW=$(shell tput setaf 3)
LIME_YELLOW=$(shell tput setaf 190)
POWDER_BLUE=$(shell tput setaf 153)
BLUE=$(shell tput setaf 4)
NORMAL=$(shell tput sgr0)

clean: ## clean out references to chart tgz's
	@cd charts/ && rm -f ./*/charts/*.tgz ./*/Chart.lock ./*/requirements.lock

k8s: ## Which kubernetes are we connected to
	@echo "Kubernetes cluster-info:"
	@kubectl cluster-info
	@echo ""
	@echo "kubectl version:"
	@kubectl version
	@echo ""
	@echo "Helm version:"
	@helm version --client

package: helm-pre-publish ## package charts
	@echo "Packaging helm charts. Any existing file won't be overwritten."; \
	mkdir -p ./tmp
	@for i in $(CHARTS); do \
		helm package charts/$${i} --dependency-update --destination ../tmp > /dev/null; \
	done; \
	mkdir -p ./repository && cp -n ../tmp/* ../repository; \
	cd ./repository && helm repo index .; \
	rm -rf ./tmp

helm-pre-build:
	@rm -f charts/ska-tango-umbrella/Chart.lock charts/ska-tango-base/Chart.lock 

k8s-post-install-chart:
	@helm get values $(RELEASE_NAME) -n $(KUBE_NAMESPACE) -o json 2>/dev/null > $(RELEASE_VALUES_FILE)
	@helm get values $(RELEASE_NAME) -n $(KUBE_NAMESPACE)

# install helm plugin from https://github.com/quintush/helm-unittest
k8s-chart-test:
	helm package charts/ska-tango-util/ -d charts/ska-tango-base/charts/; \
	mkdir -p charts/build; \
	helm unittest charts/ska-tango-base/ --with-subchart \
		--output-type JUnit --output-file charts/build/chart_template_tests.xml

k8s-pre-test:
	@echo "k8s-pre-test: setting up tests/values.yaml"
	cp charts/ska-tango-base/values.yaml tests/tango_values.yaml
	poetry export --format requirements.txt --output tests/requirements.txt --without-hashes --dev