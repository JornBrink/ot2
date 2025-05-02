"""
Directscriptmaker - V1
Author: JB
"""
#imports
import FreeSimpleGUI as sg
import os
import time
from pathlib import Path
from urllib.request import urlopen
import os
import shutil
import subprocess
import json

#import modules
from CustomModules import Selector
from CustomModules import Filedriver

#Window
dir_path = os.path.dirname(os.path.realpath(__file__))