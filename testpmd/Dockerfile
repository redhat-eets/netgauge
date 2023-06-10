FROM registry.access.redhat.com/ubi9/ubi-minimal:9.1 as dpdk-builder
ARG VER=22.11.2
USER root
RUN microdnf install -y tar xz python3 python3-pip gcc \
             kernel-devel kernel-headers libcap-devel libpcap-devel \
             libibverbs rdma-core
RUN pip3 install meson ninja pyelftools
RUN curl -L -o dpdk.tar.xz https://fast.dpdk.org/rel/dpdk-$VER.tar.xz && \
    mkdir -p /opt/dpdk && tar -xf dpdk.tar.xz && \
    cp -r dpdk*/* /opt/dpdk/ && \
    pushd /opt/dpdk && \ 
    rm -rf build && \
    meson setup --default-library=static build && cd build && ninja && \
    install -t /usr/local/bin app/dpdk-testpmd

FROM golang:1.20.5 as gobuilder
COPY . /build
WORKDIR /build/cmd
ENV GO111MODULE=on
RUN CGO_ENABLED=0 GOOS=linux go build -o runner

FROM registry.access.redhat.com/ubi9/ubi-minimal:9.1
USER root
COPY --from=gobuilder /build/cmd/runner /root/runner
COPY --from=dpdk-builder /usr/local/bin/dpdk-testpmd /usr/bin/testpmd
COPY --from=dpdk-builder /lib64/libelf-0.188.so /lib64/libelf-0.188.so
COPY --from=dpdk-builder /lib64/libpcap.so.1.10.0 /lib64/libpcap.so.1.10.0
RUN cd /lib64 && ln -sfT libelf-0.188.so libelf.so.1 && ln -sfT libpcap.so.1.10.0 libpcap.so.1
RUN microdnf install -y --setopt=tsflags=nodocs libibverbs rdma-core && \
    microdnf -y clean all --enablerepo='*'
WORKDIR /root
ENTRYPOINT ["/root/runner"]

