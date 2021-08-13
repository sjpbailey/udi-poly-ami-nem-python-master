
import udi_interface
import sys
import time
import urllib3
import xml.etree.ElementTree as ET
import re

LOGGER = udi_interface.LOGGER

class AmiNemNode(udi_interface.Node):
    def __init__(self, polyglot, primary, address, name, poly, isy, nem_oncor):
        super(AmiNemNode, self).__init__(polyglot, primary, address, name)
        self.poly = polyglot
        self.lpfx = '%s:%s' % (address,name)

        self.poly.subscribe(self.poly.START, self.start, address)
        self.poly.subscribe(self.poly.POLL, self.poll)
        
        # Attributes
        self.nem_oncor = nem_oncor
        self.isy = ISY(self.poly)
        self.poly = poly
        
    def start(self):
        if self.nem_oncor is not None:
            amiem_resp = self.isy.cmd("/rest/emeter")
            #self.setDriver('GPV', 1)

            amiem_count = 0
            amiem_count1 = 0
            ustdy_count = 0
            prevs_count = 0
            sumss_count = 0

        if amiem_resp is not None:
            amiem_root = ET.fromstring(amiem_resp)

            #amiem_count = float(amiem_root('instantaneousDemand'))
            for amie in amiem_root.iter('instantaneousDemand'):
                amiem_count = float(amie.text)
                LOGGER.info("kW: " + str(amiem_count/float(self.nem_oncor)))

            #amiem_count1 = float(amiem_root.iter('instantaneousDemand'))
            for amie1 in amiem_root.iter('instantaneousDemand'):
                amiem_count1 = float(amie1.text)
                LOGGER.info("WATTS: " + str(amiem_count1))

            #ustdy_count = float(amiem_root.iter('currDayDelivered'))
            for ustd in amiem_root.iter('currDayDelivered'):
                ustdy_count = float(ustd.text)
                LOGGER.info("kWh: " + str(ustdy_count))

            #prevs_count = float(amiem_root.iter('previousDayDelivered'))
            for prev in amiem_root.iter('previousDayDelivered'):
                prevs_count = float(prev.text)
                LOGGER.info("kWh: " + str(prevs_count))

            #sumss_count = float(amiem_root.iter('currSumDelivered')#.text)
            for sums in amiem_root.iter('currSumDelivered'):
                sumss_count = float(sums.text)
                LOGGER.info("kWh: " + str(sumss_count))
                
        
        #self.setDriver('CC', amiem_count/float(self.nem_oncor))
        #self.setDriver('GV1', amiem_count1/float(self.nem_oncor)*1000)
        #self.setDriver('TPW', ustdy_count/float(self.nem_oncor))
        #self.setDriver('GV2', prevs_count/float(self.nem_oncor))
        #self.setDriver('GV3', sumss_count/float(self.nem_oncor))


    def poll(self, polltype):
        if 'longPoll' in polltype:
            LOGGER.debug('longPoll (node)')
        else:
            LOGGER.debug('shortPoll (node)')
            if int(self.getDriver('ST')) == 1:
                self.setDriver('ST',0)
            else:
                self.setDriver('ST',1)
            LOGGER.debug('%s: get ST=%s',self.lpfx,self.getDriver('ST'))

    def cmd_ping(self,command):
        LOGGER.debug("cmd_ping:")
        r = self.http.request('GET',"google.com")
        LOGGER.debug("cmd_ping: r={}".format(r))


    def query(self,command=None):
        self.reportDrivers()

    drivers = [
        {'driver': 'ST', 'value': 0, 'uom': 2},
        {'driver': 'GPV', 'value': 0, 'uom': 2},
        {'driver': 'CC', 'value': 0, 'uom': 30},
        {'driver': 'GV1', 'value': 0, 'uom': 73},
        {'driver': 'TPW', 'value': 0, 'uom': 33},
        {'driver': 'GV2', 'value': 0, 'uom': 33},
        {'driver': 'GV3', 'value': 0, 'uom': 33},
        ]

    id = 'aminemnodeid'

    
    commands = {
                    
                    'PING': cmd_ping
        }
