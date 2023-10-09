FROM docker.io/python:3.12-rc-alpine3.17
USER root

COPY requirements.txt ./
COPY dpdk-telemetry.py /usr/bin/dpdk-telemetry.py
RUN chmod 0755 /usr/bin/dpdk-telemetry.py
RUN pip3 install -r requirements.txt
CMD ["/usr/bin/dpdk-telemetry.py"]

