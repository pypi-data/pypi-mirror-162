# PowerFlex Python Monitoring library (powerflex-monitoring)

<!-- Badges (images) related to Python package information -->
[![PyPI - Version](https://img.shields.io/pypi/v/powerflex-monitoring) ![PyPI - License](https://img.shields.io/pypi/l/powerflex-monitoring) ![PyPI - Implementation](https://img.shields.io/pypi/implementation/powerflex-monitoring) ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/powerflex-monitoring)](https://pypi.org/project/powerflex-monitoring/)

Tools to assist in monitoring a Python service.

# Installation

You can install from [PyPi](https://pypi.org/project/powerflex-monitoring/) directly:

```shellscript
pip install powerflex-monitoring
```

## Demo

See [`./demo.py`](./demo.py) for a usage example.
Also see the type hints and the docstrings.

To run the demo:

1. Install docker and docker-compose
1. Run `make up`
1. Run `docker container ls` to see the open ports and try hitting the monitoring URLs listed below

```
$ docker logs powerflex_monitoring_main
[INFO] Added route at port 8000: /monitoring/health/
[INFO] Added route at port 8000: /monitoring/ready/
[INFO] Added route at port 8000: /monitoring/metrics/
[INFO] 🚀 Starting monitoring server at port 8000
[INFO] Connected to NATS_ADDRESS nats:4222
[INFO] Configuration for NATS health check
[INFO] Service has been marked as ready. Cause: Service is initialized
```

## Feature: monitoring server

```
from powerflex_monitoring.monitoring import MonitoringServer
```

- Readiness and healthiness endpoints are at `/monitoring/ready/` and `/monitoring/health/`.
  These are useful in environments like Kubernetes: 
  https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/
- Prometheus metrics are at `/monitoring/metrics/` .
  Use the [`prometheus_client`](https://pypi.org/project/prometheus-client/) library to expose more metrics.

## Feature: NATS health checker

```
from powerflex_monitoring.nats_health_check import NatsHealthChecker
```

This class checks if NATS is healthy and marks the service as unhealthy if NATS is ever down for a certain period of time.

## Feature: wait for service to be ready

This is useful when starting your integration tests.
If you use the readiness check, then you can delay an action until your service is ready.

```
python -m powerflex_monitoring.wait_for_service_ready \
  --ready-check-url http://localhost:8000/monitoring/ready/
```

Make sure this library is installed in your virtualenv or globally,
otherwise you won't be able to run this script.

See our Makefile for an example of using this script to wait before running integration tests.

## Test results

This library is unit tested with 100% coverage in Python versions 3.8 to 3.11 and in pypy 3.9.

## Developing

1. Install the dependencies with `make setup`.
   This will use `pipenv` to manage a virtualenv.
1. Run the commands in the [`Makefile`](./Makefile) to test your code.
   Run `pipenv shell` before running the commands or run `pipenv run make ...` to run the Makefile commands with `pipenv`.
1. Please keep the unit test coverage at 100%.

# Releasing to [PyPi.org](https://pypi.org/project/powerflex-monitoring/)

1. Make sure all code checks have passed with `make commitready`.
1. Make sure you commit all code you wish to release with `git commit`.
1. Set the version in [`./src/powerflex_monitoring/VERSION`](./src/powerflex_monitoring/VERSION)
   Please attempt to follow [semantic versioning](https://semver.org/).
1. Run `make bump-version` to commit the change to the `VERSION` file.
1. Run `make release` to upload the package to pypi.org and to push a new git tag


