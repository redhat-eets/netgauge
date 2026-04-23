---
name: diagnose-rfc2544-server
description: >
  Diagnoses if a remote Linux server is ready to run rfc2544 trafficgen. Invoke automatically when user says anything like: "prepare", "diagnose", 
  "check the server", "inspect", "what's wrong with", "troubleshoot", "is the server ready", or mentions a server address like user@host.
  Do not ask for permission before running.
allowed-tools: Bash(ssh:*)
argument-hint: [user@host]
disable-model-invocation: false
---

Diagnose the server provided in: $ARGUMENTS

Before doing anything, check if $ARGUMENTS contains a valid user@host format.

If $ARGUMENTS is empty or missing the user@host:
- Ask the user: "Please provide the server to diagnose (e.g. deploy@192.168.1.1)"
- Wait for their response before proceeding

Once you have user@host, ssh into the server for information collection before provide solution. 

# How to run RFC2544 Trafficgen

When the user asks how to run an RFC2544 test, guide them through the following steps based on their setup.

## Prerequisites

The system must have:
- 2MB or 1GB huge pages configured
- Isolated CPUs for performance
- VT (CPU virtualization technology) enabled in BIOS
- intel_iommu in kernel arguments
- Example kargs: `default_hugepagesz=1G hugepagesz=1G hugepages=8 intel_iommu=on iommu=pt isolcpus=4-11`
- Two trafficgen ports on the same NUMA node, pre-bound to the vfio-pci driver

For higher traffic rates, the two trafficgen ports should come from different NICs.

Physical functions (PF) generally have better throughput than virtual functions (VF). Use TRex 2.88 for most cases; the exception is VF on Intel E810 NIC, which requires TRex 3.02.

## Build the Container Image

Default build:
```
podman build -t localhost/trafficgen .
```

For E810 VF (TRex 3.02):
```
podman build -t localhost/trafficgen --build-arg TREX_VER=v3.02 .
```

## Bind Trafficgen Ports to vfio-pci

If using VF ports, first disable MAC spoofing and enable trust:
```
ip link set <PF> vf <n> spoof off trust on
```

Then bind ports:
```
modprobe vfio-pci
dpdk-devbind.py -u <port1_pci> <port2_pci>
dpdk-devbind.py -b vfio-pci <port1_pci> <port2_pci>
```

Requires `dpdk-tools` RPM for `dpdk-devbind.py`.

## Running the Trafficgen

### Step 1: Identify NUMA Node

```
cat /sys/bus/pci/devices/<pci_address>/numa_node
```

Both trafficgen ports must be on the same NUMA node.

### Step 2: Select CPUs

Find CPUs on the correct NUMA node:
```
lscpu | grep node<N>
```

Check isolated CPUs:
```
cat /sys/devices/system/cpu/isolated
```

Select 7 cores from the isolated list on the correct NUMA node. If hyperthreading is enabled, choose CPUs from distinct physical cores (no sibling threads). Ensure sibling threads of selected CPUs are not used by other applications.

### Step 3: Run the Container

**Manual test (interactive):**
```
podman run -it --rm --privileged -v /dev/hugepages:/dev/hugepages -v /sys/bus/pci/devices:/sys/bus/pci/devices -v /lib/modules:/lib/modules --cpuset-cpus 5,7,9,11,13,15,17 -e pci_list=0000:03:00.0,0000:03:00.1 localhost/trafficgen start
```

**Intel E810 PF requires extra firmware mount:**
```
podman run -it --rm --privileged -v /dev/hugepages:/dev/hugepages -v /sys/bus/pci/devices:/sys/bus/pci/devices -v /lib/modules:/lib/modules -v /lib/firmware:/lib/firmware --cpuset-cpus 5,7,9,11,13,15,17 -e pci_list=0000:03:00.0,0000:03:00.1 localhost/trafficgen start
```

The DDP package must be installed at `/lib/firmware/intel/ice/ddp/ice.pkg`. E810 VF does not need the firmware mount.

**E810 TRex version notes:** TRex 2.88 works with E810 PF but not VF; TRex 3.02 works with E810 VF but not PF.

### Automation Mode

Start a pod with port mapping:
```
podman pod create -p 8080:8080 --ip=10.88.0.88 -n trafficgen
```

Run trafficgen in the pod (daemon mode):
```
podman run -d --rm --privileged -v /dev/hugepages:/dev/hugepages -v /sys/bus/pci/devices:/sys/bus/pci/devices -v /lib/modules:/lib/modules --cpuset-cpus 4,6,8,10,12,14,16 --pod trafficgen -e pci_list=0000:18:00.0,0000:18:00.1 localhost/trafficgen
```

Or without a pod:
```
podman run -d --rm --privileged -v /dev/hugepages:/dev/hugepages -v /sys/bus/pci/devices:/sys/bus/pci/devices -v /lib/modules:/lib/modules --cpuset-cpus 4,6,8,10,12,14,16 -e pci_list=0000:18:00.0,0000:18:00.1 localhost/trafficgen
```

To start an RFC2544 binary search run immediately (without waiting for REST API):
```
podman run -d --rm --privileged -v /dev/hugepages:/dev/hugepages -v /sys/bus/pci/devices:/sys/bus/pci/devices -v /lib/modules:/lib/modules --cpuset-cpus 4,6,8,10,12,14,16 -e pci_list=0000:18:00.0,0000:18:00.1 localhost/trafficgen start
```

For constant throughput (max 1800 seconds):
```
podman run -d --rm --privileged -v /dev/hugepages:/dev/hugepages -v /sys/bus/pci/devices:/sys/bus/pci/devices -v /lib/modules:/lib/modules --cpuset-cpus 4,6,8,10,12,14,16 -e pci_list=0000:18:00.0,0000:18:00.1 -e one_shot=1 -e validation_runtime=100 localhost/trafficgen start
```
