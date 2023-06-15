FROM docker.io/python:3.12-rc-alpine3.17
USER root

COPY dpdk-telemetry.py /usr/bin/dpdk-telemetry.py
RUN chmod 0755 /usr/bin/dpdk-telemetry.py
ENTRYPOINT ["/usr/bin/dpdk-telemetry.py"]
CMD ["-s", "/var/run/dpdk/rfc2544_trex/dpdk_telemetry.v2"]

