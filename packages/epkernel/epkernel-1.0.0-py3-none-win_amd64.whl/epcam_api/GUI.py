import os, sys, json
import ctypes
from epcam_api import epcam

def show_layer(job, step, layer):
    data = {
        'cmd': 'show_layer',
        'job': job,
        'step': step,
        'layer': layer
    }
    js = json.dumps(data)
    return epcam.view_cmd(js)
