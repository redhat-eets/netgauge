
# Testpmd with REST API

The Intel DPDK sample application [testpmd](https://doc.dpdk.org/guides/testpmd_app_ug/index.html) is commonly used on platform DPDK performance testing.

In this repository, a wrapper REST API is added to the testpmd, so that the testpmd can be remotely started/stopped/queried.

## Prerequisites:
+ 2MB or 1GB huge pages
+ isolated CPU for better performance
+ in BIOS, enable VT (cpu virtualization technology)
+ iommu enabled
+ Example kargs: `default_hugepagesz=1G hugepagesz=1G hugepages=8 intel_iommu=on iommu=pt isolcpus=4-11`
+ two testpmd ports are located on the same numa node and pre-bound to the vfio-pci driver

To achieve higher traffic rate, the two testpmd ports should come from different NICs.

## Build the container image

The container build process will download the DPDK tarball from http://core.dpdk.org/download/. By default it will download DPDK release 22.11.2.

To build the container image:
```
podman build -t testpmd:22.11.2 .
```

This image size is around 175M bytes.

The DPDK version can be changed by using `build-arg` build option, for example build 21.11.2,
```
podman build -t testpmd:21.11.2 --build-arg VER=21.11.2 .
```

To further reduce this container image size, one may choose to build the image based on the ubi-micro,
```
podman build -t testpmd-micro:22.11.2 -f Dockerfile-micro .
```

This generates an image size of 87M bytes.

`Dockerfile-micro` has dependencies on the versions of the libs used by the testpmd. This file might need to be updated with the `ubi-micro` version or DPDK version. The one in this repositry proves to work with DPDK version 22.11.2 and ubi-micro 9.1. 

## Bind testpmd ports to vfio-pci

Before running the testpmd container, the ports used by testpmd need to bind to vfio-pci. On a RHEL/Fedora system, one can install the RPM package `dpdk-tools` and then use `dpdk-devbind.py` to do the driver bind.
```
modprobe vfio-pci
dpdk-devbind.py -u <port1_pci> <port2_pci>
dpdk-devbind.py -b vfio-pci <port1_pci> <port2_pci>
```

Or simply use a DPDK container to do the job,
```
podman pull docker.io/patrickkutch/dpdk:v21.11.2
alias devbind="podman run --rm -it --privileged -v /sys/bus/pci/devices:/sys/bus/pci/devices  docker.io/patrickkutch/dpdk:v21.11.2 dpdk-devbind.py"
modprobe vfio-pci
devbind -u <port1_pci> <port2_pci>
devbind -b vfio-pci <port1_pci> <port2_pci>
```

## Podman run example

The wrapper can start the testpmd in two ways,
* auto start the testpmd
* accept client requst to start the testpmd

### Auto start the testpmd 

A typical auto start example,

```
podman run -it --rm --privileged -p 9000:9000 -v /dev/hugepages:/dev/hugepages -v /sys/bus/pci/devices:/sys/bus/pci/devices -v /lib/firmware:/lib/firmware --cpuset-cpus 4,6,8 testpmd-micro:22.11.2 --pci 0000:51:00.0 --pci 0000:51:00.1 --http-port 9000 --auto
```

This automally put the testpmd in the `io` forwarding mode. This forwarding mode normally provides the highest packet throughput number.

In the above example, the cpuset `4,6,8` is selected from the numa node 0, because the testpmd ports 0000:51:00.0 and 0000:51:00.1 are located on the numa node 0, here is how to find out which numa node the pci slot is associated with,
```
# cat /sys/bus/pci/devices/0000:51:00.0/numa_node
0
```

Next, take a look of the isolated cpu list,
```
# cat /sys/devices/system/cpu/isolated
4,6,8,10,12,14,16,18
```

Select 3 cores from the above list and make sure they are on the same numa node as the testpmd ports. For example, to see which CPUs belongs to numa node 0,
```
# cat /sys/devices/system/node/node0/cpulist
0-63
```

If the testpmd ports are physical functions (PFs) from Intel E810, then the volume mount on `/lib/firmware` is required regardless of if Intel DDP is to be used; otherwise this volume mount is not necessary.


### Control testpmd from a REST client

To start the testpmd and wait for client request,
```
podman run -it --rm --privileged -p 9000:9000 -v /dev/hugepages:/dev/hugepages -v /sys/bus/pci/devices:/sys/bus/pci/devices -v /lib/firmware:/lib/firmware --cpuset-cpus 4,6,8 testpmd-micro:22.11.2 --pci 0000:51:00.0 --pci 0000:51:00.1 --http-port 9000
```

A REST client can send request to the testpmd container to start/stop the testpmd or query for the status.

For example, to start the testpmd in `io` forwarding mode,
```
# curl -X POST localhost:9000/testpmd/start -H 'Content-Type: application/json' -d '{"mode":"io","macs":[]}'
{
    "mode": "io",
    "running": true,
    "name": "testpmd"
}
```

In the above example, the json attribute "macs" is empty for `io` mode but this field is required.

To examine the testpmd status,
```
# curl localhost:9000/testpmd/status
{
    "mode": "io",
    "running": true,
    "name": "testpmd"
}
```

To stop the testpmd from forwarding,
```
curl -X POST localhost:9000/testpmd/stop
{
    "mode": "io",
    "running": false,
    "name": "testpmd"
}
```

To list the testpmd port IDs,

```
# curl localhost:9000/testpmd/ports
[
    0,
    1
]
```

To get the MAC address from a port ID,
```
 curl localhost:9000/testpmd/mac/0
{
    "port_id": "0",
    "mac_address": "1A:BC:2F:CA:CD:62"
}
```

To get the traffic stats from a port ID,
```
# curl localhost:9000/testpmd/stats/0
{
    "port_id": "0",
    "ipackets": 7,
    "opackets": 0,
    "imissed": 0
}
```

To get information from all ports used by the testpmd,
```
# curl localhost:9000/testpmd/portsinfo
[
    {
        "port_id": 0,
        "name": "0000:18:01.0",
        "state": 1,
        "mac_addr": "1A:BC:2F:CA:CD:62",
        "numa_node": 0,
        "mtu": 1500,
        "promiscuous": 1
    },
    {
        "port_id": 1,
        "name": "0000:18:09.0",
        "state": 1,
        "mac_addr": "CE:69:CB:CF:35:2E",
        "numa_node": 0,
        "mtu": 1500,
        "promiscuous": 1
    }
]
```