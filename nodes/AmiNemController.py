

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
    class isy:
        def __init__(self, isy, poly):
            # Attributes
            self.isy = udi_interface.ISY(poly)
            self.poly = poly

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

    """
    Called via the POLL event.  The POLL event is triggerd at
    the intervals specified in the node server configuration. There
    are two separate poll events, a long poll and a short poll. Which
    one is indicated by the flag.  flag will hold the poll type either
    'longPoll' or 'shortPoll'.

    Use this if you want your node server to do something at fixed
    intervals.
    """
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
        default_nem_oncor = ""

        self.nem_oncor = self.Parameters.nem_oncor
        if self.nem_oncor is None:
            self.nem_oncor = default_nem_oncor
            LOGGER.error('check_params: Devisor for Oncor Meters not defined in customParams, please add it.  Using {}'.format(default_nem_oncor))
            self.nem_oncor = default_nem_oncor    

        # Add a notice if they need to change the user/password from the default.
        if self.nem_oncor == default_nem_oncor:
            self.Notices['auth'] = 'Please set proper divisor in configuration page for Landis+Gy set to 1000 set to 10000 for Oncor'

        # Typed Parameters allow for more complex parameter entries.
        # It may be better to do this during __init__() 

        # Lets try a simpler thing here
        self.TypedParameters.load( [
                {
                    'name': 'template_test',
                    'title': 'Test parameters',
                    'desc': 'Test parameters for template',
                    'isList': False,
                    'params': [
                        {
                            'name': 'id',
                            'title': 'The Item ID number',
                            'isRequired': True,
                        },
                        {
                            'name': 'level',
                            'title': 'Level Parameter',
                            'defaultValue': '100',
                            'isRequired': True,
                        }
                    ]
                }
            ],
            True
        )

        '''
        self.TypedParameters.load( [
                {
                    'name': 'item',
                    'title': 'Item',
                    'desc': 'Description of Item',
                    'isList': False,
                    'params': [
                        {
                            'name': 'id',
                            'title': 'The Item ID',
                            'isRequired': True,
                        },
                        {
                            'name': 'title',
                            'title': 'The Item Title',
                            'defaultValue': 'The Default Title',
                            'isRequired': True,
                        },
                        {
                            'name': 'extra',
                            'title': 'The Item Extra Info',
                            'isRequired': False,
                        }
                    ]
                },
                {
                    'name': 'itemlist',
                    'title': 'Item List',
                    'desc': 'Description of Item List',
                    'isList': True,
                    'params': [
                        {
                            'name': 'id',
                            'title': 'The Item ID',
                            'isRequired': True,
                        },
                        {
                            'name': 'title',
                            'title': 'The Item Title',
                            'defaultValue': 'The Default Title',
                            'isRequired': True,
                        },
                        {
                            'name': 'names',
                            'title': 'The Item Names',
                            'isRequired': False,
                            'isList': True,
                            'defaultValue': ['somename']
                        },
                        {
                            'name': 'extra',
                            'title': 'The Item Extra Info',
                            'isRequired': False,
                            'isList': True,
                        }
                    ]
                },
            ], True)
            '''

    
    def remove_notices_all(self,command):
        LOGGER.info('remove_notices_all: notices={}'.format(self.Notices))
        # Remove all existing notices
        self.Notices.clear()

    """
    Optional.
    Since the controller is a node in ISY, it will actual show up as a node.
    Thus it needs to know the drivers and what id it will use. The controller
    should report the node server status and have any commands that are
    needed to control operation of the node server.

    Typically, node servers will use the 'ST' driver to report the node server
    status and it a best pactice to do this unless you have a very good
    reason not to.

    The id must match the nodeDef id="controller" in the nodedefs.xml
    """
    id = 'controller'
    commands = {
        'QUERY': query,
        'DISCOVER': discover,
        'REMOVE_NOTICES_ALL': remove_notices_all,
        
    }
    drivers = [
        {'driver': 'ST', 'value': 1, 'uom': 2},
    ]
