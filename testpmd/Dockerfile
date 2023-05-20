FROM golang:1.13.4 as gobuilder
COPY . /build
WORKDIR /build/cmd/testpmd-wrapper
ENV GO111MODULE=on
RUN CGO_ENABLED=0 GOOS=linux go build


FROM registry.access.redhat.com/ubi9/ubi-minimal:9.1
USER root
COPY --from=gobuilder /build/cmd/testpmd-wrapper/testpmd-wrapper /root/testpmd-wrapper
RUN microdnf install -y dpdk dpdk-devel dpdk-tools \
        rdma-core libibverbs gettext \
    && microdnf -y clean all \ 
    && ln -s /usr/bin/dpdk-testpmd /usr/bin/testpmd \
    && curl -L -o /root/dumb-init https://github.com/Yelp/dumb-init/releases/download/v1.2.2/dumb-init_1.2.2_amd64 \
    && chmod 777 /root/dumb-init
WORKDIR /root
ENTRYPOINT ["/root/dumb-init", "--"]
CMD ["/root/testpmd-wrapper"]

