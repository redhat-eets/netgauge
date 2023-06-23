# Netgauge Project

The netgauge project develops components that are used for telco edge node user space networking performance test and telemetry data collection. The kernel networking telemetry collection is not in the scope of this project, nor is the kernel networking performance test tooling.

The user space networking performance test components include:
* [A RFC2544 traffic generator container](rfc2544/README.md) that supports REST API for remote control and data collection
* [A testpmd wrapper container](testpmd/README.md) that supports REST API for remote control and data collection

## User Space Networking Performance Test Setup

Users may choose to use either the direct connection setup, or  the switch connected setup. The direct connection setup may provide a better performance reading for user space traffic throughput and latency.

### Direct Connection
![The trafficgen and testpmd are directly connected](diagrams/RFC2544-direct-connection.png?raw=true "Direct Connection")

### Connect Through a Switch
![The trafficgen and testpmd are connected through a switch](diagrams/RFC2544-switch-connection.png?raw=true "Switch Connection")

In this switch connected setup, two VLANs are required to seperate the traffic towards the testpmd ports. In the above diagram, they are denoted as VLAN 1 and VLAN 2. 