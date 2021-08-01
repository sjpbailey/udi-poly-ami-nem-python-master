# ISY AMI NEM

The purpose of this Simple Nodeserver is to display/report, nodes for AMI Net Energy Meter within the ISY as AMI-NEM Meter.
Adds your Smart Meter in the Administrative Console instead of just in the Event Viewer.

* Supported Nodes
* Net Energy Meter
  * Instantaneous Demand Watts
  * Delivered kWh Today
  * Delivered kWh Yesterday
  * Delivered kWh Total

## Configuration

### Defaults

* "user": "User Name",
* "password": "Your ISY Password",
* "isy_ip": "host_or_IP",
* "nem_oncor": "1000"
* "polltime": "1000"

#### User Provided

* Enter your admin user name, password and IP address for the ISY controller
* Save and restart the NodeServer
