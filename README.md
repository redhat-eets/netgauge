# Netgauge Project

The netgauge project develops components that are used for telco edge node user space networking performance test and telemetry data collection. The kernel networking telemetry collection is not in the scope of this project, nor is the kernel networking performance test tooling.

The user space networking performance test components include:
* A RFC2544 traffic generator container that supports REST API for remote control and data collection
* A testpmd container that supports REST API for remote control and data collection

## User Space Networking Performance Test Setup

### Direct Connection
![The trafficgen and testpmd are directly connected](diagrams/RFC2544-direct-connection.png?raw=true "Direct Connection")

### Conneced Through a Switch
![The trafficgen and testpmd are connected through a switch](diagrams/RFC2544-switch-connection.png?raw=true "Switch Connection")