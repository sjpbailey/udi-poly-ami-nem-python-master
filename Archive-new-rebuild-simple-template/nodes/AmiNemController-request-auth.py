

"""
Get the polyinterface objects we need. 
a different Python module which doesn't have the new LOG_HANDLER functionality
"""
import udi_interface
import sys
import time
import urllib3
import requests
from requests.auth import HTTPBasicAuth
import xml.etree.ElementTree as ET
import re

"""
Some shortcuts for udi interface components

- LOGGER: to create log entries
- Custom: to access the custom data class
- ISY:    to communicate directly with the ISY (not commonly used)
"""
LOGGER = udi_interface.LOGGER
LOG_HANDLER = udi_interface.LOG_HANDLER
Custom = udi_interface.Custom
ISY = udi_interface.ISY

# IF you want a different log format than the current default
LOG_HANDLER.set_log_format('%(asctime)s %(threadName)-10s %(name)-18s %(levelname)-8s %(module)s:%(funcName)s: %(message)s')

class AmiNemController(udi_interface.Node):
    def __init__(self, polyglot, primary, address, name):
        super(AmiNemController, self).__init__(polyglot, primary, address, name)
        self.poly = polyglot
        self.name = 'AMI NEM Controller'  # override what was passed in
        self.hb = 0
        self.Parameters = Custom(polyglot, 'customparams')
        self.Notices = Custom(polyglot, 'notices')
        
        self.poly.subscribe(self.poly.START, self.start, address)
        #self.poly.subscribe(self.poly.LOGLEVEL, self.handleLevelChange)
        self.poly.subscribe(self.poly.CUSTOMPARAMS, self.parameterHandler)
        self.poly.subscribe(self.poly.POLL, self.poll)
        # Tell the interface we have subscribed to all the events we need.
        # Once we call ready(), the interface will start publishing data.
        self.poly.ready()
        # Tell the interface we exist.  
        self.poly.addNode(self)
        # Attributes
        self.user = None
        self.password = None
        self.isy_ip = None
        self.nem_oncor = None

    def parameterHandler(self, params):
        self.Parameters.load(params)
        LOGGER.debug('Loading parameters now')
        self.check_params()    
    
    def start(self):
        self.poly.updateProfile()
        self.discover()

    def get_request(self, url):
        try:
            r = requests.get(url, auth=HTTPBasicAuth(self.user, self.password))
            if r.status_code == requests.codes.ok:
                LOGGER.info(r.content)

                return r.content
            else:
                LOGGER.error("ISY-Inventory.get_request:  " + r.content)
                return None

        except requests.exceptions.RequestException as e:
            LOGGER.error("Error: " + str(e))    

    def discover(self, *args, **kwargs):
        if self.isy_ip is not None:
            self.setDriver('GPV', 1)
            amiem_url = "http://" + self.isy_ip + "/rest/emeter"
            
            amiem_count = 0
            amiem_count1 = 0
            ustdy_count = 0
            prevs_count = 0
            sumss_count = 0

        amiem_resp = self.get_request(amiem_url) #Current Demand kW
        if amiem_resp is not None:
            amiem_root = ET.fromstring(amiem_resp)
            for amie in amiem_root.iter('instantaneousDemand'):
                amiem_count = float(amie.text)
        
        amiem1_resp = self.get_request(amiem_url) #Current Demand Watts
        if amiem1_resp is not None:
            amiem1_root = ET.fromstring(amiem1_resp)
            for amie1 in amiem1_root.iter('instantaneousDemand'):
                amiem_count1 = float(amie1.text)        

        ustdy_resp = self.get_request(amiem_url) #Current Daily Delivery
        if ustdy_resp is not None:
            ustdy_root = ET.fromstring(ustdy_resp)
            for ustd in ustdy_root.iter('currDayDelivered'):
                ustdy_count = float(ustd.text)

        prevs_resp = self.get_request(amiem_url) #Previous Day Delivered
        if prevs_resp is not None:
            prevs_root = ET.fromstring(prevs_resp)
            for prev in prevs_root.iter('previousDayDelivered'):
                prevs_count = float(prev.text)     

        sumss_resp = self.get_request(amiem_url) #Sum Delivered
        if sumss_resp is not None:
            sumss_root = ET.fromstring(sumss_resp)
            for sums in sumss_root.iter('currSumDelivered'):
                sumss_count = float(sums.text)     

        #if amiem_count is not None:
        LOGGER.info("kW: " + str(amiem_count/float(self.nem_oncor)))
        LOGGER.info("WATTS: " + str(amiem_count1))
        LOGGER.info("kWh: " + str(ustdy_count))
        LOGGER.info("kWh: " + str(prevs_count))
        LOGGER.info("kWh: " + str(sumss_count))
        
        # Set Drivers
        self.setDriver('CC', amiem_count/float(self.nem_oncor))
        self.setDriver('GV1', amiem_count1/float(self.nem_oncor)*1000)
        self.setDriver('TPW', ustdy_count/float(self.nem_oncor))
        self.setDriver('GV2', prevs_count/float(self.nem_oncor))
        self.setDriver('GV3', sumss_count/float(self.nem_oncor))

    def delete(self):
        LOGGER.info('Deleting AMI NEM, Net Energy Meter')

    def stop(self):
        LOGGER.debug('AMI NEM NodeServer stopped.')

    def set_module_logs(self,level):
        LOGGER.getLogger('urllib3').setLevel(level)

    def check_params(self):
        self.Notices.clear()
        default_user = "admin"
        default_password = "YourPassword"
        default_isy_ip = "127.0.0.1"
        default_nem_oncor = "1000"
        
        self.user = self.Parameters.user
        if self.user is None:
            self.user = default_user
            LOGGER.error('check_params: user not defined in customParams, please add it.  Using {}'.format(default_user))
            self.user = default_user

        self.password = self.Parameters.password
        if self.password is None:
            self.password = default_password
            LOGGER.error('check_params: password not defined in customParams, please add it.  Using {}'.format(default_password))
            self.password = default_password
        
        self.isy_ip = self.Parameters.isy_ip
        if self.isy_ip is None:
            self.isy_ip = default_isy_ip
            LOGGER.error('check_params: IP Address not defined in customParams, please add it.  Using {}'.format(default_isy_ip))
            self.isy_ip = default_isy_ip

        self.nem_oncor = self.Parameters.nem_oncor
        if self.nem_oncor is None:
            self.nem_oncor = default_nem_oncor
            LOGGER.error('check_params: Devisor for Oncor Meters not defined in customParams, please add it.  Using {}'.format(default_nem_oncor))
            self.nem_oncor = default_nem_oncor 
        
        # Add a notice if they need to change the user/password from the default.
        if self.isy_ip == default_isy_ip:
            self.Notices['auth'] = 'Please set proper ip adress in configuration page'

    def query(self,command=None):
        nodes = self.poly.getNodes()
        for node in nodes:
            nodes[node].reportDrivers()

    def poll(self, flag):
        nodes = self.poly.getNodes()
        self.discover()
        for node in nodes:
            nodes[node].reportDrivers()
        if 'longPoll' in flag:
            LOGGER.debug('longPoll (controller)')
        else:
            LOGGER.debug('shortPoll (controller)')
            

    def remove_notices_all(self,command):
        LOGGER.info('remove_notices_all: notices={}'.format(self.Notices))
        # Remove all existing notices
        self.Notices.clear()

    id = 'controller'
    
    commands = {
        'QUERY': query,
        #'DISCOVER': discover,
        'REMOVE_NOTICES_ALL': remove_notices_all,
    }
    drivers = [
        {'driver': 'ST', 'value': 1, 'uom': 2},
        {'driver': 'GPV', 'value': "Refresh", 'uom': 2},
        {'driver': 'CC', 'value': "Refresh", 'uom': 30},
        {'driver': 'GV1', 'value': "Refresh", 'uom': 73},
        {'driver': 'TPW', 'value': "Refresh", 'uom': 33},
        {'driver': 'GV2', 'value': "Refresh", 'uom': 33},
        {'driver': 'GV3', 'value': "Refresh", 'uom': 33},
    ]
