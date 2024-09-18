# ska-tango-charts

This repository represents the bridge between the TANGO-controls framework and the kubernetes (k8s) orchestration solution. 

It defines 2 charts in order to deploy a minimal TANGO deployment in kubernetes and allow the definition of device server with the ska-tango-util helm library chart. 

## Getting started

This project uses ``make`` to provide a consistent UI (run ``make help`` for targets documentation) with a submodule. Initialize it with: 

```
git submodule update --init --recursive
```

### Install docker

Follow the instructions available at [here](https://docs.docker.com/engine/).

### Installation

You will need to install `minikube` or equivalent k8s installation in order to set up your test environment. You can follow the instruction at [here](https://gitlab.com/ska-telescope/sdi/deploy-minikube/):
```
git clone git@gitlab.com:ska-telescope/sdi/deploy-minikube.git
cd deploy-minikube
make all
```

Once minikube is installed, you can install a minimal TANGO environment with: 

```
make k8s-install-chart
```

It is possible to run some test on it with: 

```
make k8s-wait
make k8s-test
```

Finally uninstall with: 

```
make k8s-uninstall-chart
```
