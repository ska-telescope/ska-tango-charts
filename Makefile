BASE = $(shell pwd)

HELM_CHARTS ?= ska-tango-util ska-tango-base
HELM_CHARTS_TO_PUBLISH ?= $(HELM_CHARTS)

KUBE_NAMESPACE ?= ska-tango-charts#namespace to be used
RELEASE_NAME ?= test## release name of the chart
K8S_CHART = ska-tango-umbrella
MINIKUBE ?= true ## Minikube or not
ITANGO_VERSION ?= 9.5.0
CI_JOB_ID ?= local##pipeline job id
TEST_RUNNER ?= test-mk-runner-$(CI_JOB_ID)##name of the pod running the k8s_tests
TANGO_HOST ?= tango-databaseds:10000## TANGO_HOST connection to the Tango DS
TANGO_SERVER_PORT ?= 45450## TANGO_SERVER_PORT - fixed listening port for local server
K8S_CHARTS ?= ska-tango-util ska-tango-base ska-tango-umbrella## list of charts to be published on gitlab -- umbrella charts for testing purpose
CLUSTER_DOMAIN ?= cluster.local
SKA_TANGO_OPERATOR ?= false

CI_PROJECT_PATH_SLUG ?= ska-tango-charts
CI_ENVIRONMENT_SLUG ?= ska-tango-charts

K8S_CHART_PARAMS ?= --set global.minikube=$(MINIKUBE) \
	--set global.exposeDatabaseDS=$(MINIKUBE) \
	--set global.exposeAllDS=$(MINIKUBE) \
	--set global.tango_host=$(TANGO_HOST) \
	--set global.device_server_port=$(TANGO_SERVER_PORT) \
	--set global.operator=$(SKA_TANGO_OPERATOR) \
	--set global.cluster_domain=$(CLUSTER_DOMAIN)

# K8S_TEST_MAKE_PARAMS = KUBE_NAMESPACE=$(KUBE_NAMESPACE) HELM_RELEASE=$(RELEASE_NAME) TANGO_HOST=$(TANGO_HOST) MARK=$(MARK)
# K8S_CHART_PARAMS = --set global.minikube=$(MINIKUBE) --set global.tango_host=$(TANGO_HOST) --values $(BASE)/charts/values.yaml

PYTHON_VARS_BEFORE_PYTEST = PYTHONPATH=${PYTHONPATH}:/app:/app/tests KUBE_NAMESPACE=$(KUBE_NAMESPACE) HELM_RELEASE=$(RELEASE_NAME) TANGO_HOST=$(TANGO_HOST)

PYTHON_VARS_AFTER_PYTEST = --disable-pytest-warnings --timeout=300

RELEASE_SUPPORT := $(shell dirname $(abspath $(lastword $(MAKEFILE_LIST))))/.make-release-support

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

K8S_TEST_IMAGE_TO_TEST ?= artefact.skao.int/ska-tango-images-tango-itango:$(ITANGO_VERSION)

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


# install helm plugin from https://github.com/quintush/helm-unittest
k8s-chart-test:
	helm package charts/ska-tango-util/ -d charts/ska-tango-base/charts/; \
	mkdir -p charts/build; \
	helm unittest charts/ska-tango-base/ --with-subchart \
		--output-type JUnit --output-file charts/build/chart_template_tests.xml
