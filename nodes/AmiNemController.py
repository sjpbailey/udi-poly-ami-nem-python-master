

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
    def __init__(self, polyglot, primary, address, name, poly, isy):
        super(AmiNemController, self).__init__(polyglot, primary, address, name)
        self.poly = polyglot
        self.name = 'Template Controller'  # override what was passed in
        self.hb = 0

        # Attributes
        self.nem_oncor = None
        self.isy = ISY(self.poly)
        self.poly = poly

        # Create data storage classes to hold specific data that we need
        # to interact with.  
        self.Parameters = Custom(polyglot, 'customparams')
        self.Notices = Custom(polyglot, 'notices')
        self.TypedParameters = Custom(polyglot, 'customtypedparams')
        self.TypedData = Custom(polyglot, 'customtypeddata')

        # Subscribe to various events from the Interface class.  This is
        # how you will get information from Polyglog.  See the API
        # documentation for the full list of events you can subscribe to.
        #
        # The START event is unique in that you can subscribe to 
        # the start event for each node you define.

        #self.poly.subscribe(self.poly.START, self.start, address)
        #self.poly.subscribe(self.poly.LOGLEVEL, self.handleLevelChange)
        #self.poly.subscribe(self.poly.CUSTOMPARAMS, self.parameterHandler)
        #self.poly.subscribe(self.poly.CUSTOMTYPEDPARAMS, self.typedParameterHandler)
        #self.poly.subscribe(self.poly.CUSTOMTYPEDDATA, self.typedDataHandler)
        #self.poly.subscribe(self.poly.POLL, self.poll)

        # Tell the interface we have subscribed to all the events we need.
        # Once we call ready(), the interface will start publishing data.
        #self.poly.ready()

        # Tell the interface we exist.  
        self.poly.addNode(self)



    def start(self):
        """
        The Polyglot v3 Interface will publish an event to let you know you
        can start your integration. (see the START event subscribed to above)

        This is where you do your initialization / device setup.
        Polyglot v3 Interface startup done.

        Here is where you start your integration. I.E. if you need to 
        initiate communication with a device, do so here.
        """

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

    """
    Called via the CUSTOMPARAMS event. When the user enters or
    updates Custom Parameters via the dashboard. The full list of
    parameters will be sent to your node server via this event.

    Here we're loading them into our local storage so that we may
    use them as needed.

    New or changed parameters are marked so that you may trigger
    other actions when the user changes or adds a parameter.

    NOTE: Be carefull to not change parameters here. Changing
    parameters will result in a new event, causing an infinite loop.
    """
    def parameterHandler(self, params):
        self.Parameters.load(params)
        LOGGER.debug('Loading parameters now')
        self.check_params()

    
    """
    Called via the LOGLEVEL event.
    """
    def handleLevelChange(self, level):
        LOGGER.info('New log level: {}'.format(level))
    
    def query(self,command=None):
        """
        Optional.

        The query method will be called when the ISY attempts to query the
        status of the node directly.  You can do one of two things here.
        You can send the values currently held by Polyglot back to the
        ISY by calling reportDriver() or you can actually query the 
        device represented by the node and report back the current 
        status.
        """
        nodes = self.poly.getNodes()
        for node in nodes:
            nodes[node].reportDrivers()

    def discover(self, *args, **kwargs):
        self.poly.addNode(AmiNemNode(self.poly, self.address, 'aminemnodeid', 'AmiNemNode', self.poly, self.isy, self.nem_encor))

    def delete(self):
        LOGGER.info('Deleting Net Energy Meter')

    def stop(self):
        LOGGER.debug('NodeServer stopped.')

    def set_module_logs(self,level):
        logging.getLogger('urllib3').setLevel(level)

    def check_params(self):
        self.Notices.clear()
        self.Notices['hello'] = 'Hey there, my IP is {}'.format(self.poly.network_interface['addr'])
        #self.Notices['hello2'] = 'Hello Friends!'
        default_nem_oncor = None

        self.nem_oncor = self.Parameters.user
        if self.nem_oncor is None:
            self.nem_oncor = default_nem_oncor
            LOGGER.error('check_params: Divisor not defined in customParams, please add it.  Using {}'.format(default_nem_oncor))
            self.nem_oncor = default_nem_oncor

        # Add a notice if they need to change the user/password from the default.
        if self.nem_oncor == default_nem_oncor == None:
            self.Notices['auth'] = 'Please set proper Divisor for your meter type in configuration page, for Landis+Gy at 1000 set to 10000 for Oncor'

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
