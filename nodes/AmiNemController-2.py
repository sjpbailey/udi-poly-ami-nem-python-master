

"""
Get the polyinterface objects we need. 
a different Python module which doesn't have the new LOG_HANDLER functionality
"""
import udi_interface

# My Template Node
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
        self.name = 'Net Energy Meter Controller'  # override what was passed in
        self.hb = 0

        # to interact with.  
        self.Parameters = Custom(polyglot, 'customparams')
        self.Notices = Custom(polyglot, 'notices')
        self.TypedParameters = Custom(polyglot, 'customtypedparams')
        self.TypedData = Custom(polyglot, 'customtypeddata')

        self.poly.subscribe(self.poly.START, self.start, address)
        self.poly.subscribe(self.poly.LOGLEVEL, self.handleLevelChange)
        self.poly.subscribe(self.poly.CUSTOMPARAMS, self.parameterHandler)
        self.poly.subscribe(self.poly.CUSTOMTYPEDPARAMS, self.typedParameterHandler)
        self.poly.subscribe(self.poly.CUSTOMTYPEDDATA, self.typedDataHandler)
        self.poly.subscribe(self.poly.POLL, self.poll)

        # Tell the interface we have subscribed to all the events we need.
        # Once we call ready(), the interface will start publishing data.
        self.poly.ready()

        # Tell the interface we exist.  
        self.poly.addNode(self)

    def start(self):
        self.poly.updateProfile()
        self.poly.setCustomParamsDoc()
        self.discover()
    #class isy:
    #    def __init__(self, isy, poly):
            # Attributes
    #        self.isy = udi_interface.ISY(poly)
    #        self.poly = poly

    def parameterHandler(self, params):
        self.Parameters.load(params)
        LOGGER.debug('Loading parameters now')
        self.check_params()

    def typedParameterHandler(self, params):
        self.TypedParameters.load(params)
        LOGGER.debug('Loading typed parameters now')
        LOGGER.debug(params)

    def typedDataHandler(self, params):
        self.TypedData.load(params)
        LOGGER.debug('Loading typed data now')
        LOGGER.debug(params)

    """
    Called via the LOGLEVEL event.
    """
    def handleLevelChange(self, level):
        LOGGER.info('New log level: {}'.format(level))

    def poll(self, flag):
        if 'longPoll' in flag:
            LOGGER.debug('longPoll (controller)')
        else:
            LOGGER.debug('shortPoll (controller)')

    def query(self,command=None):
        nodes = self.poly.getNodes()
        for node in nodes:
            nodes[node].reportDrivers()

    def discover(self, *args, **kwargs):
        self.isy = udi_interface.ISY(poly)
        self.poly.addNode(AmiNemNode(self.poly, self.address, 'aminemnodeid', 'AmiNemNode', self.poly, self.isy, self.nem_oncor))

    def delete(self):
        LOGGER.info('Net Energy Meter deleted.')

    def stop(self):
        LOGGER.debug('NodeServer stopped.')

    def set_module_logs(self,level):
        logging.getLogger('urllib3').setLevel(level)

    def check_params(self):
        self.Notices.clear()
        #self.Notices['hello'] = 'Polisy IP is {}'.format(self.poly.network_interface['addr'])
        default_nem_oncor = "1000"

        self.nem_oncor = self.Parameters.nem_oncor
        if self.nem_oncor is None:
            self.nem_oncor = default_nem_oncor
            LOGGER.error('check_params: Devisor for Oncor Meters not defined in customParams, please add it.  Using {}'.format(default_nem_oncor))
            self.nem_oncor = default_nem_oncor    

        # Add a notice if they need to change the user/password from the default.
        if self.nem_oncor == default_nem_oncor:
            self.Notices['auth'] = 'Please set proper divisor in configuration page for Landis+Gy set to 1000 set to 10000 for Oncor'

        
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
