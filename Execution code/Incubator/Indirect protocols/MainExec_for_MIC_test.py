fileName = input("File Name: ")

#IMPORTS---------
import os
import opentrons.execute
#sourceLoc = "C:\\Users\\jornb\\OT2 left\\Development"
sourceLoc = '/var/lib/jupyter/notebooks/Development'
os.chdir(sourceLoc)
pipl = None
pipr = None
from MIC_serial_test_to_controllerlib import *
from opentrons import simulate

#READING COMMAND LIST----------
#save_folder = "C:\\Users\\jornb\\OT2 left\\Development\\Logs"
save_folder = '/var/lib/jupyter/notebooks/Development/User Inputs'
os.chdir(save_folder)
amtList, cmdList, deckMap = ReadCSV_Dat(fileName)

Answer = None
print("Whats the pipette right?(m for multichannel)")
while Answer not in ["300", "p300", "1000", "p1000", "300m", "p300m"]:
    Answer = input()
    if Answer in ["300m", "p300m"]:
        pipr = "300m"
    elif Answer in ["1000", "p1000"]:
        pipr = "1000"
    elif Answer in ["300", "p300"] :
        pipr = "300"
    else:
        print("Wrong selection detected on the right please read note 5 on instructions how to fill in. (dont capitalize the m of the multipipette or the p in p1000)")

Answer = None
print("Whats the pipette left?(m for multichannel)")
while Answer not in ["300", "p300", "1000", "p1000", "300m", "p300m"]:   
    Answer = input()
    if Answer in ["1000", "p1000"]:
        pipl = "1000"
        
    elif Answer in ["300m", "p300m"]:
        pipl = "300m"
        
    elif Answer in ["300", "p300"]:
        pipl = "300"
    else:
        print("Wrong selection detected on the left please read note 5 on instructions how to fill in. (dont capitalize the m of the multipipette or the p in p1000)")

print(pipl)

########### SIMULATE ############
#prompt simulation
simOption = input("Perform simulation? (Y/N)")
if(simOption == "Y" or simOption=="y"):
    #define protocol
    bep = simulate.get_protocol_api('2.5')
    
    #Operation
    bep.home()
    try:
        run(bep, cmdList, deckMap, amtList, pipr, pipl) 
        print("\n=====================================================\nSIMULATION COMPLETE -- EVERYTHING SEEMS OKAY (so far)\n=====================================================")
    except:
        print("Run terminated prematurely (see the last printed step)")

    #prompt continue decision
    continue_dec = input("Continue run? (Y/N)")
else:
    continue_dec = "Y"
        
    ########### EXECUTE ############
if(continue_dec == "Y" or continue_dec == "y"):
    input("Press ENTER to begin run. DON'T FORGET TO PREPARE THE ROBOT DECK")
        
        #reset values
    os.chdir(save_folder)
    amtList, cmdList, deckMap = ReadCSV_Dat(fileName)
        
        #define protocol
    bep = opentrons.execute.get_protocol_api('2.5')

        #Operation
    bep.home()
    run(bep, cmdList, deckMap, amtList, pipr, pipl)