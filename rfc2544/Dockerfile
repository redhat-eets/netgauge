FROM ubi8-minimal
ARG TREX_VER="v2.88"
USER root

RUN microdnf install dpdk dpdk-tools \
       		pciutils which \
       		gcc python3 python3-devel \
       		net-tools util-linux rdma-core libibverbs \
       		tmux gettext tar procps-ng
RUN python3 -m pip install --no-cache-dir --upgrade pip \
       && python3 -m pip install --no-cache-dir --upgrade setuptools wheel \
       && python3 -m pip install --no-cache-dir psutil jsonschema \
       && python3 -m pip install --no-cache-dir flask \
       && python3 -m pip install --no-cache-dir marshmallow \
       && python3 -m pip install --no-cache-dir waitress \
       && python3 -m pip install --no-cache-dir requests \
       && python3 -m pip install --no-cache-dir py-cputools \
       && mkdir -p /opt/trex \
       && mkdir -p /var/log/tgen \
       && mkdir -p /root/tgen \
       && curl -o /root/tgen/binary-search.py https://raw.githubusercontent.com/perftool-incubator/bench-trafficgen/main/trafficgen/binary-search.py \
       && curl -o /root/tgen/trex_tg_lib.py https://raw.githubusercontent.com/perftool-incubator/bench-trafficgen/main/trafficgen/trex_tg_lib.py \
       && curl -o /root/tgen/trex-txrx.py https://raw.githubusercontent.com/perftool-incubator/bench-trafficgen/main/trafficgen/trex-txrx.py \
       && curl -o /root/tgen/trex-query.py https://raw.githubusercontent.com/perftool-incubator/bench-trafficgen/main/trafficgen/trex-query.py \
       && curl -o /root/tgen/tg_lib.py https://raw.githubusercontent.com/perftool-incubator/bench-trafficgen/main/trafficgen/tg_lib.py \
       && curl -k -o ${TREX_VER}.tar.gz https://trex-tgn.cisco.com/trex/release/$TREX_VER.tar.gz \
       && tar xzf ${TREX_VER}.tar.gz -C /opt/trex && ln -sf /opt/trex/${TREX_VER} /opt/trex/current \
       && rm -f ${TREX_VER}.tar.gz \
       && rm -f /opt/trex/$TREX_VER/trex_client_$TREX_VER.tar.gz \
       && microdnf -y clean all --enablerepo='*'
COPY rest.py rest_schema.py trex_cfg.yaml.tmpl /root/tgen/
RUN pushd /root/tgen && popd
COPY trafficgen_entry.sh /root/
RUN chmod 777 /root/trafficgen_entry.sh /root/tgen/binary-search.py /root/tgen/trex-query.py /root/tgen/trex-txrx.py \
       && ln -f -s /bin/python3 /bin/python \
       && ln -f -s /usr/bin/python3 /usr/bin/python
COPY client.py /root/

ENTRYPOINT ["/root/trafficgen_entry.sh"]
CMD ["server", "8080"]
