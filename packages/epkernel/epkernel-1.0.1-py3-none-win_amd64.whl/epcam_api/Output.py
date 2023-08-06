import os, sys, json
from epcam_api import epcam, BASE

def save_eps(job, path):
    return BASE.save_eps(job, path)