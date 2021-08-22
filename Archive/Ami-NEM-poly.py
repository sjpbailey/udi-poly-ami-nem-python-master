#!/usr/bin/env python
"""
This is a NodeServer template for Polyglot v3 written in Python3
v2 version by Einstein.42 (James Milne) milne.james@gmail.com
v3 version by (Bob Paauwe) bpaauwe@yahoo.com
v3 Net Energy Meter by (Steve Bailey) sjpbailey@gmial.com 
"""
import udi_interface
import sys

LOGGER = udi_interface.LOGGER

""" Grab My Controller Node (optional) """
from nodes import AmiNemController

if __name__ == "__main__":
    try:
        polyglot = udi_interface.Interface([AmiNemController])
        polyglot.start()
        control = AmiNemController(polyglot, 'controller', 'controller', 'AmiNemContoller') # 'poly', 'isy', 
        polyglot.runForever()
    except (KeyboardInterrupt, SystemExit):
        LOGGER.warning("Received interrupt or exit...")
        """
        Catch SIGTERM or Control-C and exit cleanly.
        """
        polyglot.stop()
    except Exception as err:
        LOGGER.error('Excption: {0}'.format(err), exc_info=True)
    sys.exit(0)
