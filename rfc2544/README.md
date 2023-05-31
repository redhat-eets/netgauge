
# RFC2544 Performance Test Trafficgen 

RFC2544 performance test is commonly used to evaluate a system's performance when running DPDK workloads.

The container image build from this directory can be used for either automation or manual RFC2544 tests.

## Prerequisites
+ 2MB or 1GB huge pages
+ isolated CPU for better performance
+ in BIOS, enable VT (cpu virtualization technology)
+ intel_iommu in kernel argument
+ Example kargs: `default_hugepagesz=1G hugepagesz=1G hugepages=8 intel_iommu=on iommu=pt isolcpus=4-11`
+ two trafficgen ports pre-bound to vfio-pci driver.

To achieve higher traffic rate, the two trafficgen ports should come from different NICs.

In general using pysical function (PF) as the trafficgen ports can have better throughput performance than using the virtual function (VF). Building the container image based on TREX version 2.88 is recommended; the only exception is to use VF on Intel E810 nic as the trafficgen ports - in this case, building the container image based on TREX version 3.02 is recommended.   

## Openshift integration demo

[![Watch the video](https://img.youtube.com/vi/C5s9DZC3D6c/maxresdefault.jpg)](https://youtu.be/C5s9DZC3D6c)

## Podman run example for manual test

`podman run -it --rm --privileged -v /dev:/dev -v /sys:/sys -v /lib/modules:/lib/modules --cpuset-cpus 4-11 -e pci_list=0000:03:00.0,0000:03:00.1 docker.io/cscojianzhan/trafficgen`

Running the trafficgen on the PF of Intel E810 NIC requires an extra mount on /lib/firmware,
`podman run -it --rm --privileged -v /dev:/dev -v /sys:/sys -v /lib/modules:/lib/modules -v /lib/firmware:/lib/firmware --cpuset-cpus 4-11 -e pci_list=0000:03:00.0,0000:03:00.1 docker.io/cscojianzhan/trafficgen`

The default DDP package is installed under /lib/firmware for the above to work,
```
# ls ls /lib/firmware/intel/ice/ddp
ice.pkg
```

How to install the DDP packet can be found in Intel's E810 DDP package release note.

If using VF on the E810 as the trafficgen ports, then the extra mount for the DDP package is not required.

The trex version also make a different on E810. With the 2.88 trex version, the E810 PF works but VF does not; with 3.02 trex version, the E810 VF works but PF does not.
 
## Podman run example for automation

```
# start pod with port mapping
podman pod create -p 50051:50051 -n trafficgen
# start trex server in this pod
podman run -d --rm --privileged -v /dev:/dev -v /sys:/sys -v /lib/modules:/lib/modules --cpuset-cpus 4-11 --pod trafficgen -e pci_list=0000:03:00.0,0000:03:00.1  docker.io/cscojianzhan/trafficgen /root/trafficgen_entry.sh server
```

In the automation script, start the trafficgen,
`python client.py start`

To check the trafficgen status,
`python client.py status`

To get the test result,
`python client.py get-result`

To get the mac address of trafficgen test ports,
`python client.py get-mac`

## Trafficgen REST API

The trafficgen and REST API are programmed with Python. The REST API allows one to control the trafficgen.

There are several endpoints provided, allowing both query and control over the trafficgen. Below are examples using curl, but the same can be done programmatically. For more information on implementation see `rest_schema.py` and `rest.py`.

The majority of endpoints accept GET requests. Only `/trafficgen/start` accepts POST, and will take a JSON object with required fields. There is serialization present, so consult `rest_schema.py`, along with examples below, for required fields and refer to the server logs for validation errors upon incorrect schema (likely showing on the client as a `500 Internal Server Error`).

### Check if the Trafficgen is running
`curl -v http://[IP]:[PORT]/trafficgen/running`
Returns a boolean, true if running, false otherwise.

### Start the Trafficgen
```
curl -X POST http://[IP]:[PORT]/trafficgen/start -H 'Content-Type: application/json' -d '{    
    "l3":false,
    "device_pairs":"0:1",
    "search_runtime": 10,
    "validation_runtime":30,
    "num_flows":1,
    "frame_size":64,
    "max_loss_pct":0.002,
    "sniff_runtime":3,
    "search_granularity":5.0,
    "binary_search_extra_args":[]
}'
```
Returns a boolean, true if successful, false otherwise.

### Stop the Trafficgen
`curl -v http://[IP]:[PORT]/trafficgen/stop`
Returns a boolean, true if successful, false otherwise.

### Check if results are available
`curl -v http://[IP]:[PORT]/result/available`
Returns a boolean, true if available, false otherwise.

### Get results
`curl -v http://[IP]:[PORT]/result`
Returns a dict, with results if available, empty otherwise.

### Get a list of MAC addresses
`curl -v http://[IP]:[PORT]/maclist`
Returns a string of comma separated MACs if successful, an empty string otherwise.