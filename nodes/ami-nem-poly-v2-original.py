try:
    import polyinterface
except ImportError:
    import pgc_interface as polyinterface
import sys
import time
import requests
from requests.auth import HTTPBasicAuth
import xml.etree.ElementTree as ET
import re

LOGGER = polyinterface.LOGGER
class Controller(polyinterface.Controller):
    def __init__(self, polyglot):
        super(Controller, self).__init__(polyglot)
        self.name = 'AMI-NEM Meter'
        self.user = None
        self.password = None
        self.isy_ip = None
        self.nem_oncor = None
        self.debug_enable = 'True'
        self.poly.onConfig(self.process_config)

    def start(self):
        if 'debug_enable' in self.polyConfig['customParams']:
            self.debug_enable = self.polyConfig['customParams']['debug_enable']
        self.heartbeat(0)
        if self.check_params():
            self.discover()

    def shortPoll(self):
        self.discover()

    def longPoll(self):
        self.heartbeat()

    def query(self, command=None):
        self.discover()

    def get_request(self, url):
        try:
            r = requests.get(url, auth=HTTPBasicAuth(self.user, self.password))
            if r.status_code == requests.codes.ok:
                if self.debug_enable == 'True' or self.debug_enable == 'true':
                    print(r.content)

                return r.content
            else:
                LOGGER.error("ISY-Inventory.get_request:  " + r.content)
                return None

        except requests.exceptions.RequestException as e:
            LOGGER.error("Error: " + str(e))
      
    def discover(self, *args, **kwargs):
        if self.isy_ip is not None:
            amiem_url = "http://" + self.isy_ip + "/rest/emeter"
            
            amiem_count = 0
            amiem_count1 = 0
            ustdy_count = 0
            prevs_count = 0
            sumss_count = 0

        amiem_resp = self.get_request(amiem_url)
        if amiem_resp is not None:
            amiem_root = ET.fromstring(amiem_resp)
            for amie in amiem_root.iter('instantaneousDemand'):
                amiem_count = float(amie.text)
        
        amiem1_resp = self.get_request(amiem_url)
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

        sumss_resp = self.get_request(amiem_url) #Previous Day Delivered
        if sumss_resp is not None:
            sumss_root = ET.fromstring(sumss_resp)
            for sums in sumss_root.iter('currSumDelivered'):
                sumss_count = float(sums.text)     
            
            
        if self.debug_enable == 'True' or self.debug_enable == 'true':
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
        
        if amiem_count is not None:
            self.setDriver('GPV', 1)
        pass
        
    def delete(self):
        LOGGER.info('Removing AMI-NEM Meter')

    def stop(self):
        LOGGER.debug('NodeServer stopped.')

    def process_config(self, config):
        # this seems to get called twice for every change, why?
        # What does config represent?
        LOGGER.info("process_config: Enter config={}".format(config));
        LOGGER.info("process_config: Exit");

    def heartbeat(self, init=False):
        # LOGGER.debug('heartbeat: init={}'.format(init))
        if init is not False:
            self.hb = init
        # LOGGER.debug('heartbeat: hb={}'.format(self.hb))
        if self.hb == 0:
            self.reportCmd("DON", 2)
            self.hb = 1
        else:
            self.reportCmd("DOF", 2)
            self.hb = 0

    def check_params(self):
        st = True
        self.remove_notices_all()
        default_user = "YourUserName"
        default_password = "YourPassword"
        default_isy_ip = "127.0.0.1"
        default_nem_oncor = "1000"

        if 'user' in self.polyConfig['customParams']:
            self.user = self.polyConfig['customParams']['user']
        else:
            self.user = default_user
            LOGGER.error('check_params: user not defined in customParams, please add it.  Using {}'.format(self.user))
            st = False

        if 'password' in self.polyConfig['customParams']:
            self.password = self.polyConfig['customParams']['password']
        else:
            self.password = default_password
            LOGGER.error(
                'check_params: password not defined in customParams, please add it.  Using {}'.format(self.password))
            st = False

        if 'isy_ip' in self.polyConfig['customParams']:
            self.isy_ip = self.polyConfig['customParams']['isy_ip']
        else:
            self.isy_ip = default_isy_ip
            LOGGER.error(
                'check_params: ISY IP not defined in customParams, please add it.  Using {}'.format(self.isy_ip))
            st = False
        
        if 'nem_oncor' in self.polyConfig['customParams']:
            self.nem_oncor = self.polyConfig['customParams']['nem_oncor']
        else:
            self.nem_oncor = default_nem_oncor
            LOGGER.error(
                'check_params: ISY IP not defined in customParams, please add it.  Using {}'.format(self.nem_oncor))
            st = False

        if 'debug_enable' in self.polyConfig['customParams']:
            self.debug_enable = self.polyConfig['customParams']['debug_enable']

        # Make sure they are in the params
        self.addCustomParam({'password': self.password, 'user': self.user,
                            'isy_ip': self.isy_ip, 'nem_oncor': self.nem_oncor, 'debug_enable': self.debug_enable})

        # Add a notice if they need to change the user/password from the default.
        if self.user == default_user or self.password == default_password or self.isy_ip == default_isy_ip: #or self.nem_oncor == default_nem_oncor
            self.addNotice('Please set proper user, password and ISY IP '
                            'in configuration page, and restart this nodeserver')
            st = False

        if st:
            return True
        else:
            return False

    def remove_notices_all(self):
        LOGGER.info('remove_notices_all: notices={}'.format(self.poly.config['notices']))
        # Remove all existing notices
        self.removeNoticesAll()

    def update_profile(self, command):
        LOGGER.info('update_profile:')
        st = self.poly.installprofile()
        return st

    id = 'controller'
    commands = {
        #'COVT': setPerkW,
        'QUERY': query,
        'DISCOVER': discover,
        'UPDATE_PROFILE': update_profile,
    }
    drivers = [
                {'driver': 'GPV', 'value': 0, 'uom': 2},
                {'driver': 'CC', 'value': 1, 'uom': 30},
                {'driver': 'GV1', 'value': 1, 'uom': 73},
                {'driver': 'TPW', 'value': 1, 'uom': 33},
                {'driver': 'GV2', 'value': 1, 'uom': 33},
                {'driver': 'GV3', 'value': 1, 'uom': 33},
                        
    ]


if __name__ == "__main__":
    try:
        polyglot = polyinterface.Interface('AMI-NEM Meter')
        polyglot.start()
        control = Controller(polyglot)
        control.runForever()
    except (KeyboardInterrupt, SystemExit):
        LOGGER.warning("Received interrupt or exit...")
        polyglot.stop()
    except Exception as err:
        LOGGER.error('Excption: {0}'.format(err), exc_info=True)
    sys.exit(0)

### sjb 09_07_2019 ###