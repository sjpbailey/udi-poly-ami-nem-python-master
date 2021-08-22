
# ISY Net Energy Meter

![NetEnergyMeter](https://github.com/sjpbailey/udi-poly-ami-nem-python-master/blob/master/Images/AMI_NEM_Poly_2.png)

## Added Watts for Instaneous Demand

![WattADDED](https://github.com/sjpbailey/udi-poly-ami-nem-python-master/blob/master/Images/Update_Add_Watts.png)

The purpose of this Simple Nodeserver is to display/report, nodes for AMI Net Energy Meter within the ISY as AMI-NEM Meter.
Adds your Smart Meter in the Administrative Console instead of just in the Event Viewer.

* Supported Nodes
* Net Energy Meter
* Instantaneous Demand Watts
* Delivered kWh Today
* Delivered kWh Yesterday
* Delivered kWh Total

### Configuration

#### Defaults

* Default Short Poll:  Every 5 minutes
* Default Long Poll: Every 10 minutes (heartbeat)
* nem_oncor: Input your Meter type, 1000 for Landis+Gyr, 10000 for Oncor Meters

##### User Provided

* nem_oncor: Input your Meter type, 1000 for Landis+Gyr, 10000 for Oncor Meters
* Save and restart the NodeServer
