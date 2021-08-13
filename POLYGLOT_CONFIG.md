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

* "nem_oncor": "1000"

#### User Provided

* Enter your Meters Divisor, for the Your Meter Type 10000 for Oncor, 1000 for Landis+Gyr Meters
* Save and restart the NodeServer
