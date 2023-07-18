FROM registry.access.redhat.com/ubi9/ubi-minimal:9.1 as dpdk-builder
ARG VER=22.11.2
USER root
RUN microdnf install -y tar xz python3 python3-pip gcc \
             kernel-devel kernel-headers \
             libpcap-devel \
             numactl-devel libibverbs rdma-core
RUN pip3 install meson ninja pyelftools
RUN curl -L -o dpdk.tar.xz https://fast.dpdk.org/rel/dpdk-$VER.tar.xz && \
    mkdir -p /opt/dpdk && tar -xf dpdk.tar.xz && \
    cp -r dpdk*/* /opt/dpdk/ && \
    pushd /opt/dpdk && \ 
    rm -rf build && \
    meson setup --default-library=static -Dplatform=generic build && \
    cd build && ninja && \
    install -t /usr/local/bin app/dpdk-testpmd

FROM public.ecr.aws/docker/library/golang:1.20.5 as gobuilder
COPY . /build
WORKDIR /build/cmd
ENV GO111MODULE=on
RUN CGO_ENABLED=0 GOOS=linux go build -o runner

FROM registry.access.redhat.com/ubi9/ubi-minimal:9.1
USER root
COPY --from=gobuilder /build/cmd/runner /root/runner
COPY --from=dpdk-builder /usr/local/bin/dpdk-testpmd /usr/bin/testpmd
RUN microdnf install -y --setopt=tsflags=nodocs numactl-libs libibverbs rdma-core libpcap elfutils-libelf && \
    microdnf -y clean all --enablerepo='*'
WORKDIR /root
ENTRYPOINT ["/root/runner"]

