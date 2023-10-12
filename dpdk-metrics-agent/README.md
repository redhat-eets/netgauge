# DPDK Telemetry Agent

The DPDK telemetry agent is designed to collect the DPDK traffic metrics where the kernel-based network metrics collector cannot be applied.

## DPDK telemetry API

By default, every DPDK application creates a socket with the path `<runtime_directory>/dpdk_telemetry.<version>`, unless it is disabled during the application's build process. For more details, interested users are encouraged to refer to: https://doc.dpdk.org/guides/howto/telemetry.html.

This agent uses this socket to acquire DPDK traffic metrics from DPDK applications. Through this socket, the agent can monitor a DPDK application's traffic metrics without the need for instrumenting the application.

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
![Agent sidecar as a prometheus scraping point](../diagrams/dpdk-telemetry-prometheus-scraping.jpg?raw=true "Prometheus Scraping")

For demonstration purposes, you can use the sample pod manifest file located at `manifests/single-node-openshift/pod-dpdk-telemetry.yaml` to start a sample pod with the telemetry agent as a sidecar. To allow Prometheus access to the sidecar, you'll need a service pointing to it. For simplicity, let's set up a node port service using the sample service manifest found at `manifests/single-node-openshift/service-dpdk-telemetry.yaml`. Once the sample pod and service are running, launch a Prometheus instance and configure it to scrape from the node port. Here is a sample Prometheus configuration for scraping data from the node port:
```
scrape_configs:
  - job_name: "dpdk-telemetry"

    scrape_interval: 5s

    static_configs:
      - targets: ['192.168.222.30:31264']
        labels:
          group: 'k8s-demo'
```

In the provided Probemtheus configuration, the IP address `192.168.222.30:31264` corresponds to the node port defined in the service manifest.

The DPDK telemetry agent can also integrate with an OpenTelemetry collector. In the diagram below, the agent is deployed as a sidecar in the same pod alongside the DPDK application container. It uses OTLP to export the DPDK traffic metrics to the OpenTelemetry collector.
![Agent sidecar exporting metrics to a open telemetry collector](../diagrams/dpdk-telemetry-otlp.jpg?raw=true "Open Telemetry Collector")

For demonstration purposes, you can use the sample configuration file located at `manifests/open-telemetry/otel-collector-config.yaml` to start an OpenTelemetry collector outside of the Kubernetes cluster using the following command:
```
podman run --rm -p 4317:4317 -v $PWD/manifests/open-telemetry/otel-collector-config.yaml:/etc/otel-collector-config.yaml otel/opentelemetry-collector:latest  --config=/etc/otel-collector-config.yaml
```

Next, utilize the sample pod manifest file located at `manifests/single-node-openshift/pod-dpdk-telemetry-otlp.yaml` to start a sample pod with the telemetry agent as a sidecar. When using this sample manifest file, don't forget to update the `--otlp-url` setting to point to your actual OpenTelemetry collector.

The OpenTelemetry collector should generate console logs when the DPDK telemetry agent exports metrics to it. Sample logs might look like this:
```
StartTimestamp: 2023-10-12 14:39:59.956169198 +0000 UTC
Timestamp: 2023-10-12 15:00:26.11248955 +0000 UTC
Value: 712
NumberDataPoints #4
Data point attributes:
     -> app: Str(testpmd)
     -> port: Int(1)
     -> stats: Str(ibytes)
StartTimestamp: 2023-10-12 14:39:59.956169198 +0000 UTC
Timestamp: 2023-10-12 15:00:26.11248955 +0000 UTC
Value: 60068
NumberDataPoints #5
Data point attributes:
     -> app: Str(testpmd)
     -> port: Int(1)
     -> stats: Str(ipackets)
StartTimestamp: 2023-10-12 14:39:59.956169198 +0000 UTC
Timestamp: 2023-10-12 15:00:26.11248955 +0000 UTC
Value: 712
NumberDataPoints #6
Data point attributes:
     -> app: Str(testpmd)
     -> port: Int(1)
     -> stats: Str(obytes)
StartTimestamp: 2023-10-12 14:39:59.956169198 +0000 UTC
Timestamp: 2023-10-12 15:00:26.11248955 +0000 UTC
Value: 291853
NumberDataPoints #7
Data point attributes:
     -> app: Str(testpmd)
     -> port: Int(1)
     -> stats: Str(opackets)
```




