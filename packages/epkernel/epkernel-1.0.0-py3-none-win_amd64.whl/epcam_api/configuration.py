import os, sys, json
from epcam_api import epcam, BASE

def init(): 
    epcam.init()
    config_path = os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'bin'), 'config')
    BASE.set_config_path(config_path)





