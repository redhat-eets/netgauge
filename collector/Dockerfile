FROM ubi8-minimal
USER root

RUN microdnf -y --setopt=tsflags=nodocs install python3 && \
    microdnf -y clean all --enablerepo='*'
COPY dpdk-port-stats.py /usr/bin/dpdk-port-stats.py
RUN chmod 0755 /usr/bin/dpdk-port-stats.py
ENTRYPOINT ["/usr/bin/dpdk-port-stats.py"]
CMD ["-s", "/var/run/dpdk/rfc2544_trex/dpdk_telemetry.v2"]

