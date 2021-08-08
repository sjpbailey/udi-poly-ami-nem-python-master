
import udi_interface
import sys
import time
import urllib3
import requests
from requests.auth import HTTPBasicAuth
import xml.etree.ElementTree as ET
import re

LOGGER = udi_interface.LOGGER
LOG_HANDLER = udi_interface.LOG_HANDLER

class AmiNemNode(udi_interface.Node):
    def __init__(self, polyglot, primary, address, name, isy_ip, user, password, nem_oncor):
        super(AmiNemNode, self).__init__(polyglot, primary, address, name)
        self.poly = polyglot
        self.lpfx = '%s:%s' % (address,name)

        self.poly.subscribe(self.poly.START, self.start, address)
        self.poly.subscribe(self.poly.POLL, self.poll)
        self.isy_ip = isy_ip
        self.user = user
        self.password = password
        self.nem_oncor = nem_oncor

    def get_request(self, url):
        try:
            r = requests.get(url, auth=HTTPBasicAuth("http://" + self.isy_ip + self.user + self.password + "/rest/emeter"))
            if r.status_code == requests.codes.ok:
                LOGGER.info(r.content)

                return r.content
            else:
                LOGGER.error("ISY-Inventory.get_request:  " + r.content)
                return None

        except requests.exceptions.RequestException as e:
            LOGGER.error("Error: " + str(e))
    
    def start(self):
        if self.isy_ip is not None:
            self.setDriver('GPV', 1)
            amiem_url = "url" #"http://" + self.isy_ip + "/rest/emeter"
            
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

    def poll(self, polltype):
        self.query()
        self.reportDrivers()
        LOGGER.debug('shortPoll (node)')

    def query(self,command=None):
        self.reportDrivers()
        
    
    drivers = [
        {'driver': 'GPV', 'value': 0, 'uom': 2},
        {'driver': 'CC', 'value': 0, 'uom': 30},
        {'driver': 'GV1', 'value': 0, 'uom': 73},
        {'driver': 'TPW', 'value': 0, 'uom': 33},
        {'driver': 'GV2', 'value': 0, 'uom': 33},
        {'driver': 'GV3', 'value': 0, 'uom': 33},
            ]
    
    id = 'aminemnodeid'
    
    commands = {
                    'QUERY': query
                }
