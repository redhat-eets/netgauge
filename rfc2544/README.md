
# RFC2544 Performance Test Trafficgen

RFC2544 performance testing is commonly used to evaluate a system's performance when running DPDK workloads.

The container image build from this directory can be used for either automation or manual RFC2544 tests.

## Prerequisites
+ 2MB or 1GB huge pages
+ isolated CPU for better performance
+ in BIOS, enable VT (cpu virtualization technology)
+ intel_iommu in kernel argument
+ Example kargs: `default_hugepagesz=1G hugepagesz=1G hugepages=8 intel_iommu=on iommu=pt isolcpus=4-11`
+ two trafficgen ports are located on the same numa node and pre-bound to the vfio-pci driver.

To achieve higher traffic rate, the two trafficgen ports should come from different NICs.

In general using pysical function (PF) as the trafficgen ports can have better throughput performance than using the virtual function (VF). Building the container image based on TRex version 2.88 is recommended; the only exception is to use VF on Intel E810 nic as the trafficgen ports - in this case, building the container image based on TRex version 3.02 is recommended.

## Build the container image

To build with the default TREX_VERSION,
```
podman build -t localhost/trafficgen .
```

To build with a different TREX_VERSION, say for the purpose of running it on the virtual function on E810,
```
podman build -t localhost/trafficgen --build-arg TREX_VERSION=3.02 .
```

## Bind trafficgen port to vfio-pci

Before running the trafficgen container, the trafficgen ports need to be bound to vfio-pci first. Assume the RPM package `dpdk-tools` is pre-installed on the system, and `dpdk-devbind.py` is available with this RPM install. Here is the steps to bind the ports to the vfio-pci,
```
modprobe vfio-pci
dpdk-devbind.py -u <port1_pci> <port2_pci>
dpdk-devbind.py -b vfio-pci <port1_pci> <port2_pci>
```

## Podman run example for manual test

First, identify the numa node associated with the trafficgen port PCI slot,
```
cat /sys/bus/pci/devices/<pci_address>/numa_node
```

Note: the two trafficgen ports should be associated with the same numa node, otherwise the trafficgen won't work.

Next, select a cpuset from this numa node. For example, if the trafficgen ports are associated with numa node 1, then take a look of the cpu list on this numa node,
```
# lscpu | grep node1
NUMA node1 CPU(s):   1,3,5,7,9,11,13,15,17,19,21,23,25,27,29,31,33,35,37,39,41,43,45,47,49,51,53,55,57,59,61,63,65,67,69,71,73,75,77,79
```

Also note the isolated cpu list,
```
# cat /sys/devices/system/cpu/isolated
4-19
```

If the isolated cpu list from the above command is empty, then [follow the prerequisites section](#Prerequisites) to fix it.

Select 7 cores from the isolated cpu list and make sure the selected cores are from numa node 1. For example, here "5,7,9,11,13,15,17" could be used.

For manual test, users normally do not use pod, but run the trafficgen container directly,
```
podman run -it --rm --privileged -v /dev/hugepages:/dev/hugepages -v /sys/bus/pci/devices:/sys/bus/pci/devices -v /lib/modules:/lib/modules --cpuset-cpus 5,7,9,11,13,15,17 -e pci_list=0000:03:00.0,0000:03:00.1 localhost/trafficgen start
```

Running the trafficgen on the PF of Intel E810 NIC requires an extra volume mount on `/lib/firmware`,
```
podman run -it --rm --privileged -v /dev/hugepages:/dev/hugepages -v /sys/bus/pci/devices:/sys/bus/pci/devices -v /lib/modules:/lib/modules -v /lib/firmware:/lib/firmware --cpuset-cpus 5,7,9,11,13,15,17 -e pci_list=0000:03:00.0,0000:03:00.1 localhost/trafficgen start
```

The default DDP package is required to be installed under `/lib/firmware` for the above to work,
```
# ls /lib/firmware/intel/ice/ddp
ice.pkg
```

How to install the DDP packet can be found in Intel's E810 DDP package release note.

If using VF on the E810 as the trafficgen ports, then the extra volume mount of `/lib/firmware` for the DDP package is not required.

Note: the TRex version makes a difference on E810. With the 2.88 TRex version, the E810 PF works but VF does not; with 3.02 TRex version, the E810 VF works but PF does not.

## Podman run example for automation

In a kubernetest enviroment, a container runs inside a pod. To emulate this, user could first start a pod, then run the trafficgen container in the pod. Here are the emulation steps.

First, start the pod with port mapping (8080 for our WSGI server) and a static IP (if desired):
```
podman pod create -p 8080:8080 --ip=10.88.0.88 -n trafficgen
```

Start the TRex server in the above pod using the container image we built:
```
podman run -d --rm --privileged -v /dev/hugepages:/dev/hugepages -v /sys/bus/pci/devices:/sys/bus/pci/devices -v /lib/modules:/lib/modules --cpuset-cpus 4,6,8,10,12,14,16 --pod trafficgen -e pci_list=0000:18:00.0,0000:18:00.1 localhost/trafficgen
```

If users do not want to emulate the pod, they may choose to directly start the trafficgen container without using a pod,
```
podman run -d --rm --privileged -v /dev/hugepages:/dev/hugepages -v /sys/bus/pci/devices:/sys/bus/pci/devices -v /lib/modules:/lib/modules --cpuset-cpus 4,6,8,10,12,14,16 --pod trafficgen -e pci_list=0000:18:00.0,0000:18:00.1 localhost/trafficgen
```

Note: in the above example, the cpuset is from numa node 0. This is because the trafficgen ports used in this example are associated with numa node 0.

## Trafficgen REST API

The trafficgen and REST API are programmed with Python. The REST API allows one to control the trafficgen.

There are several endpoints provided, allowing both query and control over the trafficgen. Below are examples using curl, but the same can be done programmatically. For more information on implementation see `rest_schema.py` and `rest.py`.

The majority of endpoints accept GET requests. Only `/trafficgen/start` accepts POST, and will take a JSON object with required fields. There is serialization present, so consult `rest_schema.py`, along with examples below, for required fields and refer to the server logs for validation errors upon incorrect schema (likely showing on the client as a `500 Internal Server Error`).

This is built using [Flask](https://github.com/pallets/flask/) as the REST API Framework, [marshmallow](https://github.com/marshmallow-code/marshmallow) for serialization, and [Waitress](https://github.com/Pylons/waitress) as the WSGI server.

### Check if the Trafficgen is running
```curl -v http://[IP]:8080/trafficgen/running```

Returns a boolean, true if running, false otherwise.

### Start the Trafficgen

```
curl -X POST http://localhost:8080/trafficgen/start -H 'Content-Type: application/json' -d '{
    "l3":false,
    "device_pairs":"0:1",
    "search_runtime": 10,
    "validation_runtime":30,
    "num_flows":1000,
    "frame_size":64,
    "max_loss_pct":0.002,
    "sniff_runtime":10,
    "search_granularity":5.0,
    "teaching_warmup_packet_type":"generic",
    "teaching_warmup_packet_rate":10000,
    "use_src_ip_flows":1,
    "use_dst_ip_flows":1,
    "use_src_mac_flows":0,
    "use_dst_mac_flows":0,
    "send_teaching_warmup": true,
    "rate_tolerance": 10,
    "runtime_tolerance": 10,
    "rate": 50,
    "rate_unit": "%",
    "no_promisc": true
}'
```

Returns a boolean, true if successful, false otherwise.

### Stop the Trafficgen
```curl -v http://[IP]:8080/trafficgen/stop```

Returns a boolean, true if successful, false otherwise.

### Check if results are available
```curl -v http://[IP]:8080/result/available```

Returns a boolean, true if available, false otherwise.

### Get results
```curl -v http://[IP]:8080/result```

Returns a dict, with results if available, empty otherwise.

### Get a list of MAC addresses
```curl -v http://[IP]:8080/maclist```

Returns a string of comma separated MACs if successful, an empty string otherwise.

## Trafficgen REST API Client

The trafficgen REST API features `client.py` that can be used to interface with the trafficgen utilizing the API. Various modes exist for the client, outlined below, which can take either CLI arguments or use the default values present in the code. A mode is required to run the client, and all of the modes have two required arguments: `server-addr` and `server-port` corresponding to the running trafficgen server.

### start

The start mode starts the trafficgen running. It utilizes the `/trafficgen/start` endpoint.

Example run:

```
python3 client.py start --server-addr 10.88.0.88 --server-port 8080
start trafficgen: success
```

### stop

The stop mode stops the trafficgen from running. It utilizes the `trafficgen/stop` endpoint.

Example run:

```
python3 client.py stop --server-addr 10.88.0.88 --server-port 8080
stop trafficgen: success
```

### status

The status mode gets the status of the trafficgen and report file. It utilizes the `trafficgen/running` and `result/available` endpoints.

Example run:

```
python3 client.py status --server-addr 10.88.0.88 --server-port 8080
trafficgen is currently not running
test result is avalable: yes
```

### get-result

The get-result mode gets the result file. It utilizes the `/result` endpoint.

Example run:

```
python3 client.py get-result --server-addr 10.88.0.88 --server-port 8080
{'0': {'rx_l1_bps': 9992899070.524572, 'rx_l2_bps': 7137785050.374695, 'rx_latency_average': 171.0, 'rx_latency_maximum': 3725.0, 'rx_latency_minimum': 8.0, 'rx_pps': 14870385.521613948, 'tx_l1_bps': 9992899070.524572, 'tx_l2_bps': 7137785050.374695, 'tx_pps': 14870385.521613948}, '1': {'rx_l1_bps': 9992899070.524572, 'rx_l2_bps': 7137785050.374695, 'rx_latency_average': 172.0, 'rx_latency_maximum': 3725.0, 'rx_latency_minimum': 6.0, 'rx_pps': 14870385.521613948, 'tx_l1_bps': 9992899070.524572, 'tx_l2_bps': 7137785050.374695, 'tx_pps': 14870385.521613948}}
port 0 rx_pps: 14870385.52
port 0 rx_latency_average: 171.00
port 1 rx_pps: 14870385.52
port 1 rx_latency_average: 172.00

```

### get-mac

The get-mac mode gets the MAC address list. It utilizes the `/maclist` endpoint.

Example run:

```
python3 client.py get-mac --server-addr 10.88.0.88 --server-port 8080
This trafficgen mac list: 00:11:22:33:44:55,aa:bb:cc:ee:ff:00
```

### auto

The auto mode will automatically run the test, checking for results, and printing the json report to stdout. This allows for further parsing, and bypasses other print statements (except for error handling), allowing for automation. 

This mode will run with all default values if no other arguments are set. However, please note that the `timeout` is specific to auto mode and should be adjusted if timeouts are observed. This mode also allows for bypassing the majority of the CLI arguments when `config` is set. This will look for a JSON formatted config file which contains the arguments one wishes to override. The example template, `auto_client.yaml.tmpl`, sets the `timeout` and `max_loss_pct` fields to non-default values.

Upon successful run auto mode should return a single line to stdout: the result JSON.

Example minimal run:

```
python3 client.py auto --server-addr 10.88.0.88 --server-port 8080
{'0': {'rx_l1_bps': 9992899070.524572, 'rx_l2_bps': 7137785050.374695, 'rx_latency_average': 171.0, 'rx_latency_maximum': 3725.0, 'rx_latency_minimum': 8.0, 'rx_pps': 14870385.521613948, 'tx_l1_bps': 9992899070.524572, 'tx_l2_bps': 7137785050.374695, 'tx_pps': 14870385.521613948}, '1': {'rx_l1_bps': 9992899070.524572, 'rx_l2_bps': 7137785050.374695, 'rx_latency_average': 172.0, 'rx_latency_maximum': 3725.0, 'rx_latency_minimum': 6.0, 'rx_pps': 14870385.521613948, 'tx_l1_bps': 9992899070.524572, 'tx_l2_bps': 7137785050.374695, 'tx_pps': 14870385.521613948}}
```