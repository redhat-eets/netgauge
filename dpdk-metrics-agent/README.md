# DPDK Telemetry Agent

The DPDK telemetry agent is designed to collect the DPDK traffic metrics where the kernel-based network metrics collecor cannot be applied.

## DPDK telemetry API

By default, every DPDK application creates a socket with the path `<runtime_directory>/dpdk_telemetry.<version>`, unless it is disabled during the application's build process. For more details, interested users are encouraged to refer to: https://doc.dpdk.org/guides/howto/telemetry.html.

This agent uses this socket to aquire DPDK traffic metrics from DPDK applications. Through this socket, the agent can monitor a DPDK application's traffic metrics without the need for instrumenting the application.

## Backend support

* Prometheus
* OpenTelemetry Collector

## Agent command line options

* --sock-prefix, DPDK telemetry socket directory
* --port, prometheus scraping port
* --backend, 1: prometheus, 2: open telemetry collector
* --otlp-url, URL to the open telemetry collector GRPC endpoint
* --interval, time interval in seconds for metric collection

## Agent deployment in kubernetes

The DPDK telemetry agent can integrate with either Prometheus or OpenTelemetry collector as its backend.

In the diagram below, the agent is deployed as a sidecar in the same pod alongside the DPDK application container, offering a scraping point for Prometheus.
![Agent deployed sidecar as a prometheus scraping point](../diagrams/dpdk-telemetry-prometheus-scraping.jpg?raw=true "Prometheus Scraping")

In the diagram below, the agent is deployed as a sidecar in the same pod alongside the DPDK application container. It uses OTLP to exports the DPDK traffic metrics to the OpenTelemetry collector.
![Agent deployed sidecar as a prometheus scraping point](../diagrams/dpdk-telemetry-otlp.jpg?raw=true "Prometheus Scraping")



