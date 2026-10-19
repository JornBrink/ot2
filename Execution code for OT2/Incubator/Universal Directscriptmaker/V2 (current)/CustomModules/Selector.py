#protocol selector is the selector for what protocol to run on what robot.
#scope: Find robot on pc, get IP, get name robot (active), load protocol and database it
#import modules
import os
import json
import FreeSimpleGUI as sg

# =============================================================================
# FUNCTIONS
# =============================================================================
def _load_discovery_robots():
    """
    Load robot entries from both the Opentrons (Flex) and Opentrons OT2 
    discovery.json files, merging them into a single list.
    Returns an empty list if neither file is found.
    """
    userpath = os.path.expanduser("~")
    paths = [
        os.path.join(userpath, "AppData", "Roaming", "Opentrons", "discovery.json"),
        os.path.join(userpath, "AppData", "Roaming", "Opentrons OT2", "discovery.json"),
    ]
    robots = []
    for p in paths:
        try:
            with open(p) as f:
                robots.extend(json.load(f)['robots'])
        except FileNotFoundError:
            pass  # that app version simply isn't installed, skip it
        except Exception as e:
            print(f"Error reading {p}: {e}")
    return robots


def Robotdetails(simulation):
    json_data = _load_discovery_robots()

    if not json_data:
        sg.Popup(
            "No Opentrons app discovery file found.\n"
            "Make sure the Opentrons or Opentrons OT2 app is installed and has been opened at least once.",
            keep_on_top=True
        )
        return None, None, None

    names = addresses = robot_type = None

    for current_data in json_data:
        status = current_data['addresses'][0]['seen']

        if status and simulation != '1':
            names      = current_data['name']
            addresses  = current_data['addresses'][0]['ip']
            robot_type = current_data['health']['robot_model']
            break  # stop at the first active robot

        elif not status and simulation == '1':
            names      = current_data['name']
            addresses  = current_data['addresses'][0]['ip']
            robot_type = current_data['health']['robot_model']
            break

    if robot_type is None:
        sg.Popup(
            "The robot is offline -- restart the robot and this program (after the robot is ready)",
            keep_on_top=True
        )
        return None, None, None

    robot_type = "Flex" if "OT-3" in robot_type else "OT2"

    return names, addresses, robot_type


def protocolfinder(simulation, robot_type):
    #first 
    userpath = os.path.expanduser("~")
    
    #simulation block
    if simulation == "1":
        #If simulation = 1 all files should be detected
        restpath = os.getcwd() +  '//Directscripts'
        #since simulation gives access to everthing this needs to be done with a bit of an interesting route
        filelist = []
        for root, dirs, files in os.walk(restpath):
            for name in files:
                filelist.append(name)
    else:
        #production version
        restpath = userpath + "//Desktop//Directscriptmaker//_internal//Directscripts//" + robot_type
        filelist = os.listdir(restpath)
     
    return filelist


def protocolselector(simulation, robot_type, selection):
    userpath = os.path.expanduser("~")
    
    if simulation == "1":
        #If simulation = 1 all files should be detected
        restpath = os.path.dirname(os.path.realpath(__file__)) +'//Directscripts//'
        #since simulation gives access to everthing this needs to be done with a bit of an interesting route
        for root, dirs, files in os.walk(restpath):
            for root, dirs, files in os.walk(restpath):
                for file in files:
                    if file == selection:
                        truename = os.path.join(root, file)
                        return truename
    else:
        #production version
        restpath = userpath + "//Desktop//_internal//Directscripts//" + robot_type + "//" + selection
        return None  # If no file matches