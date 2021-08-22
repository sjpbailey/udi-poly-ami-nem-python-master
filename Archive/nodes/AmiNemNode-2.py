
import udi_interface
import sys
import time
import urllib3
import xml.etree.ElementTree as ET

LOGGER = udi_interface.LOGGER
ISY = udi_interface.ISY
class AmiNemNode(udi_interface.Node):
    def __init__(self, polyglot, primary, address, name, poly, isy, nem_oncor):
        super(AmiNemNode, self).__init__(polyglot, primary, address, name)
        self.poly = polyglot
        self.lpfx = '%s:%s' % (address,name)
        
        # Attributes
        self.poly = poly
        self.isy = isy
        self.nem_oncor = nem_oncor

        self.poly.subscribe(self.poly.START, self.start, address)
        self.poly.subscribe(self.poly.POLL, self.poll)

    def start(self):
        isy = udi_interface.ISY()
        amiem_resp = self.isy.cmd("/rest/emeter")

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
                self.setDriver('CC', amiem_count/float(self.nem_oncor))
                
            #amiem_count1 = float(amiem_root.iter('instantaneousDemand'))
            for amie1 in amiem_root.iter('instantaneousDemand'):
                amiem_count1 = float(amie1.text)
                LOGGER.info("WATTS: " + str(amiem_count1))
                #self.setDriver('GV1', amiem_count1/float(self.nem_oncor)*1000)

            #ustdy_count = float(amiem_root.iter('currDayDelivered'))
            for ustd in amiem_root.iter('currDayDelivered'):
                ustdy_count = float(ustd.text)
                LOGGER.info("kWh: " + str(ustdy_count))
                #self.setDriver('TPW', ustdy_count/float(self.nem_oncor))

            #prevs_count = float(amiem_root.iter('previousDayDelivered'))
            for prev in amiem_root.iter('previousDayDelivered'):
                prevs_count = float(prev.text)
                LOGGER.info("kWh: " + str(prevs_count))
                #self.setDriver('GV2', prevs_count/float(self.nem_oncor))

            #sumss_count = float(amiem_root.iter('currSumDelivered')#.text)
            for sums in amiem_root.iter('currSumDelivered'):
                sumss_count = float(sums.text)
                LOGGER.info("kWh: " + str(sumss_count))
                #self.setDriver('GV3', sumss_count/float(self.nem_oncor))
        if amiem_count is not None:
            self.setDriver('GPV', 1)
        pass        
        #self.http = urllib3.PoolManager()

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

    def query(self,command=None):
        self.reportDrivers()
        LOGGER.debug("cmd_query:")

    """
    Optional.
    This is an array of dictionary items containing the variable names(drivers)
    values and uoms(units of measure) from ISY. This is how ISY knows what kind
    of variable to display. Check the UOM's in the WSDK for a complete list.
    UOM 2 is boolean so the ISY will display 'True/False'
    """
    drivers = [
        {'driver': 'ST', 'value': 0, 'uom': 2},
        {'driver': 'GPV', 'value': 0, 'uom': 2},
        {'driver': 'CC', 'value': 0, 'uom': 30},
        {'driver': 'GV1', 'value': 0, 'uom': 73},
        {'driver': 'TPW', 'value': 0, 'uom': 33},
        {'driver': 'GV2', 'value': 0, 'uom': 33},
        {'driver': 'GV3', 'value': 0, 'uom': 33},
        ]

    """
    id of the node from the nodedefs.xml that is in the profile.zip. This tells
    the ISY what fields and commands this node has.
    """
    id = 'aminemnodeid'

    """
    This is a dictionary of commands. If ISY sends a command to the NodeServer,
    this tells it which method to call. DON calls setOn, etc.
    """
    commands = {
                    
                    'PING': query
                }
