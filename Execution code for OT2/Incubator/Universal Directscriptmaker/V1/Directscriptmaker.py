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
from CustomModules import Protocolcustomizer

#Window
def Mainwindow(simulation, protocollist):
    layout = [
         [sg.B("Make commandlist"), sg.B("Refresh")],
         [sg.T("Please provide information about the run you want to do")],
         [sg.T('Select a file', s=(10,1)), sg.FileBrowse(file_types=(('CSV Files', '*.csv'),), key='Browse')],
         [sg.T('Or use the one you just made')],
         [sg.R("Selected", "group1", key="Selected", default = True), sg.R("Made", "group1", key="Made")],
         [sg.T("Experiment Name", s = (15,1)), sg.I(key='ExpName')],
         [sg.T("Your Name", s = (15,1)), sg.I(key = 'Name')],
         [sg.T('Date (yymmdd)', s = (15,1)),sg.I(key = 'date')],
         [sg.T("What experiment are you running?")],
         [sg.Listbox(protocollist, size = (50, 4), key = "protocol")],
         [sg.T('Sarstedt or Greiner (only 48 wellplates)')],
         [sg.R('Sarstedt', 'group6', key = 'brands'), sg.R('Greiner', 'group6', key ='brandg')],
         [sg.B('Save', s= 16, button_color = 'black on yellow'), sg.B('Send', disabled = True, s= 16), sg.P(), sg.B('Close', s=16, button_color = 'tomato')]
         ]
    return sg.Window('Directscript maker', layout, finalize = True) 




def filesending():
    layout = [
        [sg.Text("Please provide all information below")],
        [sg.Text("Choose your file: "), sg.FileBrowse(key = 'Browse')],                                                   
        [sg.Text("Platemap PMID"), sg.InputText('', size=(56, 1), key = 'PMID')],                                         
        [sg.Text("Your name (First AND Lastname)"), sg.InputText('', size=(41, 1), key = 'Firstlast')],                  
        [sg.Text("Experiment Name"), sg.InputText('', size=(54, 1), key = 'EXPname')],                                       
        [sg.Text("Experiment number"), sg.InputText('', size=(53, 1), key = 'EXPnum')],                                    
        [sg.Text("What type of experiment are you going to do?")],
        [sg.Radio("Checkerboard", "group1", key = 'Checker'), 
         sg.Radio("Multiplate MIC", "group1", key = 'MVP'), 
         sg.Radio("384 well plate", "group1", key = '384p'), 
         sg.Radio("M9MixR", "group1", key = 'M9MixR'),
         sg.Radio("48 Well plate", "group1", key = '48w'),
         sg.Radio("SingleplateMIC", "group1", key= 'Sp')],                                                             
        [sg.Text("Do you want to fill outer wells in robot? (384 plate only)")],
        [sg.Radio("Yes", "group3", key = 'Fill'), sg.Radio("No", "group3", key = 'nFill', default = False)],
        [sg.Button("Save User Inputs", s= 16, button_color = 'black on yellow'), 
         sg.Button("Send to Server", s= 16, disabled = True), sg.Push(), sg.Button("Close", s= 16, button_color = "tomato")]
        ]
    return sg.Window("Webdriver", layout, finalize= True)


#start with checking if the Simconfig file exists.
dir_path = os.path.dirname(os.path.realpath(__file__))
simpath = dir_path + "//CustomModules//"
if os.path.isfile(simpath + "Simconfig.py"):
    from CustomModules.Simconfig import *
else:
    simulation = "0"

#Getting the details of the robot
robotname, robotip, robot_type = Selector.Robotdetails(simulation)
#getting the protocols for the robot
protocollist = Selector.protocolfinder(simulation, robot_type)

#put the theming in (Sim:Green, Flex:lightPurple, OT2:Darkblue)
if simulation == "1":
    sg.theme("DarkGreen1")
elif robot_type == "Flex":
    sg.theme("LightPurple")
    pc = "Flex"
else:
    sg.theme('DarkBlue3')
    pc = "OT2"
    
window1 = Mainwindow(simulation, protocollist)
window2_active = False

#Start window loop
while True:
    window, event, values = sg.read_all_windows()
    
    #Stops everything when user uses the button cancel or closes the window
    if event == 'Close' or  event == sg.WIN_CLOSED:
        if window2_active == True:
            window2_active = False
            window2.close()
            window1.UnHide()
        if window == window1:
            window.close()
            break
    
    if event == 'Make commandlist':
        window2_active = True
        window2 = filesending()
        window1.Hide()
        
    
    if event == 'Save':
        #save event triggers only on window1. Goal: save user input and start preperations for sending the csv
        experimentname = values.get("ExpName")
        usrname = values.get("Name")
        date = values.get("date")
        cmdfilename = values.get("Browse")
        directscript = values.get("protocol")
        directscript = directscript[0]
        directscriptname = date + "_" + usrname + "_" + experimentname + ".py"
        basepath = os.getcwd()
        print(basepath)