

"""
Get the polyinterface objects we need. 
a different Python module which doesn't have the new LOG_HANDLER functionality
"""
import udi_interface
import sys
import time
import requests
from requests.auth import HTTPBasicAuth
import xml.etree.ElementTree as ET
import re

# My AMI NEM Net Energy Meter Node
from nodes import AmiNemNode

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
        self.zone_query_delay_ms = self.Parameters.polltime #Custom(polyglot, 'polltime') #"1000"
        #self.TypedParameters = Custom(polyglot, 'customtypedparams')

        # Subscribe to various events from the Interface class.  This is
        # how you will get information from Polyglog.  See the API
        # documentation for the full list of events you can subscribe to.
        #
        # The START event is unique in that you can subscribe to 
        # the start event for each node you define.

        self.poly.subscribe(self.poly.START, self.start, address)
        self.poly.subscribe(self.poly.LOGLEVEL, self.handleLevelChange)
        self.poly.subscribe(self.poly.CUSTOMPARAMS, self.parameterHandler)
        #self.poly.subscribe(self.poly.CUSTOMTYPEDPARAMS, self.typedParameterHandler)
        self.poly.subscribe(self.poly.POLL, self.poll)

        # Tell the interface we have subscribed to all the events we need.
        # Once we call ready(), the interface will start publishing data.
        self.poly.ready()

        # Tell the interface we exist.  
        self.poly.addNode(self)

    def start(self):
        # Send the profile files to the ISY if neccessary. The profile version
        # number will be checked and compared. If it has changed since the last
        # start, the new files will be sent.
        self.poly.updateProfile()

        # Send the default custom parameters documentation file to Polyglot
        # for display in the dashboard.
        self.poly.setCustomParamsDoc()

        # Initializing a heartbeat is an example of something you'd want
        # to do during start.  Note that it is not required to have a
        # heartbeat in your node server
        self.heartbeat(0)

        # Device discovery. Here you may query for your device(s) and 
        # their capabilities.  Also where you can create nodes that
        # represent the found device(s)
        self.discover()

        # Here you may want to send updated values to the ISY rather
        # than wait for a poll interval.  The user will get more 
        # immediate feedback that the node server is running
    
    def parameterHandler(self, params):
        self.Parameters.load(params)
        self.check_params()

    def typedParameterHandler(self, params):
        self.TypedParameters.load(params)

    def handleLevelChange(self, level):
        LOGGER.info('New log level: {}'.format(level))

    def poll(self, flag):
        if 'longPoll' in flag:
            LOGGER.debug('longPoll (controller)')
            self.heartbeat()
            self.reportDrivers()
        else:
            LOGGER.debug('shortPoll (controller)')
        
        """timeout = self.zone_query_delay_ms #int(self.zone_query_delay_ms)
        nodes = self.poly.getNodes()
        for node in nodes:
            if isinstance(nodes[node], AmiNemNode):
                nodes[node].query()
                nodes[node].reportDrivers()
                self.discover()
                time.sleep(10)"""

    def query(self,command=None):
        self.discover()
        nodes = self.poly.getNodes()
        for node in nodes:
            nodes[node].reportDrivers()

    def discover(self, *args, **kwargs):
        if self.isy_ip is not None:
            self.poly.addNode(AmiNemNode(self.poly, self.address, 'aminemnodeid',
            'Net Energy Meter', self.isy_ip, self.user, self.password, self.nem_oncor))

    def delete(self):
        LOGGER.info('Deleting AMI NEM, Net Energy Meter')

    def stop(self):
        LOGGER.debug('AMI NEM NodeServer stopped.')

    def heartbeat(self,init=False):
        LOGGER.debug('heartbeat: init={}'.format(init))
        if init is not False:
            self.hb = init
        LOGGER.debug('heartbeat: hb={}'.format(self.hb))
        if self.hb == 0:
            self.reportCmd("DON",2)
            self.hb = 1
        else:
            self.reportCmd("DOF",2)
            self.hb = 0

    def set_module_logs(self,level):
        LOGGER.getLogger('urllib3').setLevel(level)   ### Line was logging.getLogger('urllib3').setLevel(level) logging is not recognized? Logging also does not manually set in polyglot?

    def check_params(self):
        self.Notices.clear()
        default_user = "YourUserName"
        default_password = "YourPassword"
        default_isy_ip = "127.0.0.1"
        default_nem_oncor = "1000"
        #default_polltime = "1000"

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

        """self.polltime = self.Parameters.polltime
        if self.polltime is None:
            self.polltime = default_polltime
            LOGGER.error('check_params: Poll Timer in ms not defined in customParams, please add it.  Using {}'.format(default_polltime))
            self.polltime = default_polltime"""      
        
        # Add a notice if they need to change the user/password from the default.
        if self.user == default_user or self.password == default_password:
            self.Notices['auth'] = 'Please set proper user and password in configuration page'

    def remove_notices_all(self,command):
        LOGGER.info('remove_notices_all: notices={}'.format(self.Notices))
        # Remove all existing notices
        self.Notices.clear()

    id = 'controller'
    commands = {
        'QUERY': query,
        'DISCOVER': discover,
        'REMOVE_NOTICES_ALL': remove_notices_all,
    }
    drivers = [
        {'driver': 'ST', 'value': 1, 'uom': 2},
        
    ]
