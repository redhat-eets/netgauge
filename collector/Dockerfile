FROM docker.io/python:3.12-rc-alpine3.17
USER root

COPY dpdk-port-stats.py /usr/bin/dpdk-port-stats.py
RUN chmod 0755 /usr/bin/dpdk-port-stats.py
ENTRYPOINT ["/usr/bin/dpdk-port-stats.py"]
CMD ["-s", "/var/run/dpdk/rfc2544_trex/dpdk_telemetry.v2"]

