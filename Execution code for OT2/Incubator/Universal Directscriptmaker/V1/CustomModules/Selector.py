#protocol selector is the selector for what protocol to run on what robot.
#scope: Find robot on pc, get IP, get name robot (active), load protocol and database it
#imports Directscripts

#import modules
import os
import json

#functions
#function Robots
def Robotdetails(simulation):
    userpath = os.path.expanduser("~")
    robotloc = userpath + "//AppData//Roaming//Opentrons//discovery.json"
    try:
        f = open(robotloc)
        
    except:
        print("Error in the selector module -- Robotdetails")
        
    json_data = json.load(f)['robots']
        
    # initiate loop

    # get IP address for each robot
    for i in range(len(json_data)):
        # subset json data for current robot
        current_data = json_data[i]
        
        #since only one pc can controll 1 robot, remove everything that is not seen. Only simulation gives something
        status = (current_data['addresses'][0]['seen'])
        if status != False and simulation != '1':
            names = (current_data['name'])
            addresses = (current_data['addresses'][0]['ip'])
            status = (current_data['addresses'][0]['seen'])
            robot_type = current_data['health']
            #[health] is a dict  so turned into list then added technically no list or anythin is needed
            robot_type = robot_type[0]['robot_model']
                  
    return names, addresses, robot_type


def protocolselector(simulation):
    #first 
    userpath = os.path.expanduser("~")
    