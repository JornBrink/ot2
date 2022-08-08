#INPUTS------------Do not touch ANYTHING but the mainInput
fileName = "Halving_CommandList.csv"

# =============================================================================

#update: 20/07/2022

#IMPORTS---------
import csv
import numpy as np
from math import pi
from opentrons import protocol_api
import os
import opentrons.execute

####### CUSTOM LIBRARY #########
def ReadCSV_Dat(file_name):
    #save all read info into the variable: command_list
    #possible that for "normal" operation (with normal csv)
    
    content_list = np.empty(10)
    #print(content_list)
    with open(file_name, 'r') as file:
        try: #Tries to first get 9 column with ; as delimiter
            cmdCSV = csv.reader(file, delimiter=';')
            #print(cmdCSV)
            for cmdRow in cmdCSV:
                # print(cmdRow)
                content_list = np.vstack([content_list, cmdRow])
                #print("delimiter tries ;")
        except: #if ; doesnt work it will try it with , as delimiter
            cmdCSV = csv.reader(file,delimiter=',')
            for cmdRow in cmdCSV:
                content_list = np.vstack([content_list, cmdRow])
                #print("delimiter tries ,")

    #Find starting point of amount list and command list
    indices = []
    for a in range(len(content_list)):
        if(">" in content_list[a][0]):
            indices.append(a)

    #get amount list of liquids in the first few rows csv
    amt_list = content_list[indices[0]+1:indices[1]]
    amt_list = [x[[0, 1, 2, 4]] for x in amt_list]
    
    #get command list under the amount lists
    cmd_list = content_list[indices[1]+1:indices[2]]
    
    #get input deck map
    inp_deckMap = content_list[indices[2]+1:]
    
    #parse out deck location and fills
    deck_loc = [x[0] for x in inp_deckMap]
    fill = [x[1] for x in inp_deckMap]
    deck_map = {}
    for i in range(len(deck_loc)):
        if("96" in fill[i] or "eep" in fill[i] or "48" in fill[i] or "384" in fill[i]):
            if('eep' in fill[i]):
                fill[i] = "nest_96_wellplate_2ml_deep"
            elif("96" in fill[i]):
                fill[i] = "nest_96_wellplate_200ul_flat"
            elif("48" in fill[i]):
                fill[i] = "greinerbioone677102_48_wellplate_1000ul"
            else:
                #fill[i] = "greiner_384_wellplate_115ul"
                fill[i] = "corning_384_wellplate_112ul_flat"

        elif('15' in fill[i]):
            fill[i] = "opentrons_15_tuberack_falcon_15ml_conical"
        elif('50' in fill[i] or "olvent" in fill[i] or "nno" in fill[i] or "SOLVENT" in fill[i] or "eservoir" in fill[i]):
            if('50' in fill[i] or "olvent" in fill[i] or "nno" in fill[i] or "SOLVENT" in fill[i]):
                fill[i] = "opentrons_6_tuberack_falcon_50ml_conical"
            else:
                fill[i] = "nest_12_reservoir_15ml"

        elif('dorf' in fill[i] or 'tock' in fill[i] or "1.5" in fill[i]):
            fill[i] = "opentrons_24_tuberack_nest_1.5ml_snapcap"
        
        elif('TRASH' in fill[i]):
            fill[i]= "TRASH"
            
        elif('empty'in fill[i]):
            fill[i]= "empty"    
        else:
            if("1000" in fill[i]):
                fill[i] = "opentrons_96_tiprack_1000ul"
            elif("300m" in fill[i]):
                #tiprack_300s = "opentrons_96_tiprack_300ul"
                fill[i] = "tiprack_300m"
            else:
                #tiprack_300m = "opentrons_96_tiprack_300ul"
                fill[i]= "tiprack_300s"

        deck_map[deck_loc[i]] = fill[i]
        
    return amt_list, cmd_list, deck_map

def Update_Source(amt_list, cmd_line, source_well, current_transAmt):
    #get tube location
    tube_loc = [(x[0]==cmd_line[0] and x[1]==source_well) for x in amt_list]
    tube_loc = [i for i, x in enumerate(tube_loc) if x]

    #get source amount after dispensed
    if('eservoir' in amt_list[tube_loc[0]][4]):
        amt_list[tube_loc[0]][3] = float(amt_list[tube_loc[0]][3]) - current_transAmt*8
    else:
        amt_list[tube_loc[0]][3] = float(amt_list[tube_loc[0]][3]) - current_transAmt
    print(amt_list[tube_loc[0]][3])
    return(amt_list)

def Update_Target(amt_list, cmd_line, target_well, deck_map, current_transAmt):
    #get tube location
    tube_loc = [(x[0]==cmd_line[2] and x[1]==target_well) for x in amt_list]
    tube_loc = [i for i, x in enumerate(tube_loc) if x]
    #print(tube_loc)
#if tube is not yet registered
    if(len(tube_loc)==0):
        #check target ware type
        ware_type = deck_map[cmd_line[2]]
        
        if('96_wellplate' in ware_type):
            type_target = '96-well'
        elif('1.5ml' in ware_type):
            type_target = '1.5ml_eppendorf'
        elif('eep' in ware_type):
            type_target = '96-deepwell'
        elif("eservoir" in ware_type):
            type_target = "nest_12_reservoir_15ml"
        else:
            type_target = '15ml_falcon'
        
        #generate next item
        regItem = [cmd_line[2], #target labware
                   target_well, #target slot/well
                   "New_Item", #name
                   current_transAmt, #initial amount in slot/well
                   type_target] #type of well/slot
        #append
        amt_list.append(regItem)
        #print(amt_list.append(regItem))
   
    else:
        #get source amount after dispensed
        amt_list[tube_loc[0]][3] = float(amt_list[tube_loc[0]][3]) + current_transAmt   
    
    return(amt_list)

def CalTip_Aspirate(solutions_map, cmd_line, source_well):
    #get tube type
    tube_loc = [(x[0]==cmd_line[0] and x[1]==source_well) for x in solutions_map]
    tube_loc = [i for i, x in enumerate(tube_loc) if x]
    tube_type = solutions_map[tube_loc[0]][4]
    
    #get source amount after aspirated
    src_amt = float(solutions_map[tube_loc[0]][3])
        
    #print(tube_type)
    #if not 96 well plate
    if(("50" in tube_type, "15" in tube_type, "1,5" in tube_type) and ("eservoir" not in tube_type)):
        #get dimensions
        if("50" in tube_type):
            h_bot = 15.88 #mm
            r = 28.14/2 #mm
            minH = 5 #mm
            stab = 7 #mm
       
        elif("15" in tube_type):
            h_bot = 23.36 #mm
            r = 15.62/2 #mm
            minH = 5 #mm
            stab = 5 #mm
        else:
            #Tube Dimensions - Eppendorf
            h_bot = 37.8-20 #mm
            r = 8.7/2 #mm
            minH = 2
            stab = 5 #mm

        #calculate height
        Vmax_bot = pi*r**2*h_bot/3
        
        if(src_amt>Vmax_bot):
            if(src_amt > (Vmax_bot + 50) and ("1.5" in tube_type)):
                h_tip = 17 # hard-code location for eppendorfs
            else:
                h_tip = h_bot + (src_amt - Vmax_bot)/(pi*r**2)
        else:
            if("1.5" in tube_type):
                h_tip = 5 # hard-code location for eppendorfs
            else:
                h_tip = ((3*src_amt*h_bot**2)/(pi*r**2))**(1/3)
    
    #if source is a 96-well plate
    elif("96" in tube_type):
        r = 6.45/2 #mm
        minH = 2 #mm
        h_tip = src_amt/(pi*r**2) 
        
    #if source is a nest reservoir
    elif( "eservoir" in tube_type):
        h_tip = src_amt /8.2/73.2 #volume with a mm stap
        stab = 10
        minH = 2
        #h_tip = 10
        #print("Patrick was here")
        #print(src_amt)
        #print(h_tip)  
    else:
    #deep well dimensions
        h_bot = 0
        r = 8.5/2 #mm
        minH = 2 #mm
        stab = 4 #mm
        
            #add extra distance; place minimum height into place
    h_tip = max(h_tip-stab, minH)

    return(h_tip)

def CalTip_Dispense(solutions_map, cmd_line, target):
    #get tube type
    tube_loc = [(x[0]==cmd_line[2] and x[1]==target) for x in solutions_map]
    tube_loc = [i for i, x in enumerate(tube_loc) if x]
    tube_type = solutions_map[tube_loc[0]][4]
    
    #get source amount after dispensed
    src_amt = float(solutions_map[tube_loc[0]][3])
    
    #if not 96 well plate
    if('96-well' not in tube_type):
        #get dimensions
        if("50" in tube_type):
            h_bot = 15.88 #mm
            r = 28.14/2 #mm
            minH = 5 #mm
        elif("15" in tube_type):
            h_bot = 23.36 #mm
            r = 15.62/2 #mm
            minH = 4 #mm
        elif("1.5" in tube_type):
            #Tube Dimensions - Eppendorf
            h_bot = 37.8-20 #mm
            r = 8.7/2 #mm
            minH = 2
        else:
            #deep well dimensions
            h_bot = 0
            r = 8.5/2 #mm
            minH = 1 #mm
        
        #calculate height
        Vmax_bot = pi*r**2*h_bot/3
        
        if(src_amt>Vmax_bot):
            h_tip = h_bot + (src_amt - Vmax_bot)/(pi*r**2)
        else:
            h_tip = ((3*src_amt*h_bot**2)/(pi*r**2))**(1/3)
    
    #if ource is a 96-well plate
    else:
        #on top of well
        h_tip = 6 #mm
        minH = 6 #mm
    
    #add extra distance; place minimum height into place
    h_tip = max(h_tip+3, minH)
    
    return(h_tip)

def GetSrcVolume(solutions_map, cmd_line, source_well):
    #get tube type
    tube_loc = [(x[0]==cmd_line[0] and x[1]==source_well) for x in solutions_map]
    tube_loc = [i for i, x in enumerate(tube_loc) if x]
    tube_type = solutions_map[tube_loc[0]][4]

    #get source amount after aspirated
    src_amt = float(solutions_map[tube_loc[0]][3])
    
    return src_amt

#METADATA----------
metadata = {
    'protocolName': 'MIC serial to controller',
    'author': 'Sebastian <sebastian.tandar@gmail.com>' 'Jorn <jornbrink@kpnmail.nl>',
    'description': '96 wells plate MIC with p300 possibility' 'somewhat universal script',
    'apiLevel': '2.12'
}

############# MAIN #############
def run(protocol: protocol_api.ProtocolContext):
    global fileName #calling from global
    #search for where the user input it. Possible to use for jupyter. not really nessesary to use
    try:
        os.chdir('C://Users//jornb//Documents//GitHub//ot2new//Execution code for OT2//Incubator//Test User inputs')

    except:
        os.chdir('/var/lib/jupyter/notebooks/User Inputs')
        
    amtList, cmdList, deckMap = ReadCSV_Dat(fileName)
    
###########################  LOAD LABWARES   ###########################
    tipLocs_300s = []
    tipLocs_300m = []
    tipLocs_1000 = []
    
    for i in range(11):
        #load actual labware
        labware_name = deckMap["labware_"+str(i+1)]
        if (('empty' not in labware_name) and labware_name != 'TRASH'):
            deck_position = int(list(deckMap.keys())[i].split("_")[1])
            try:
                globals()[list(deckMap.keys())[i]] = protocol.load_labware(labware_name, deck_position)
            except:
                globals()[list(deckMap.keys())[i]] = protocol.load_labware("opentrons_96_tiprack_300ul", deck_position)
        
            #if labware is a tip rack, assign number to tip location(s)
            if("tiprack" in labware_name or "tip" in labware_name):
                if("1000" in labware_name):
                    tipLocs_1000.append(globals()[list(deckMap.keys())[i]])
                elif("300m" in labware_name):
                    tipLocs_300m.append(globals()[list(deckMap.keys())[i]])
                else:
                    tipLocs_300s.append(globals()[list(deckMap.keys())[i]])
                
    #first check which pipettes are listed as active to load them
    Pipette = cmdList[8]
    
    #load pipettes right is hardcoded for now
    right_pipette = protocol.load_instrument('p300_single_gen2', 'right', tip_racks = tipLocs_300s)
    
    #left can be a bit more switching
    if("p1000" in Pipette or "P1000" in Pipette or "p1" in Pipette or "P1" in Pipette):
        left_pipette = protocol.load_instrument('p1000_single_gen2', 'left', tip_racks= tipLocs_1000)
        #combine the pipettes in pipette_caller
        pipette_caller = {"p1000" : left_pipette, "p300" : right_pipette}
    else:
        left_pipette = protocol.load_instrument('p300_multi_gen2', 'left', tip_racks= tipLocs_300m)
        pipette_caller = {"p300m" : left_pipette, "p300" : right_pipette}   
    
    print(left_pipette)
    print(right_pipette)
    ########################### Start Tip counter ####################
    tip_counter = [ 0, 0] # p300, p300m or p1000 depending on CMD list
    current_tip = 0
    
    ########################### EXECUTE ##############################
    #first work through all commands
    current_tipID = 0 #initiate tip ID
    iterateMarker = -1
    progressMax = len(cmdList)

    for i in range(len(cmdList)):
        #subset
        cmdRow = cmdList[i]
        print("Progress\t: " + str(int(round(i/progressMax*100))) + "%")
        print(cmdRow)

        #parse all informations
        source_ware = cmdRow[0]
        source_well = cmdRow[1].split(', ')
        target_ware = cmdRow[2]
        target_well = cmdRow[3].split(', ')
        transfer_amt = float(cmdRow[4]) #only one transfer amount is allowed
        if(float(cmdRow[5]) > 0):
            mix_amt = max(float(cmdRow[5]), 300)
        else:
            mix_amt = 0
        tipID = int(cmdRow[6])
        
        c_step= cmdList[i]
        try:
            n_step=cmdList[i+1]
        except:
            print("Job done")
        
        
# =============================================================================
#         #create current source_well (multi source operations)
#         for x in range(len(source_well)):
#             current_source_well = source_well[x]
# 
#             #iterate through all target wells
#             for j in range(len(target_well)):
#                 current_target= target_well[j]
#                 print(current_target)
#                 print(current_source_well)
# =============================================================================
            
            
            
            
            
            
            
            
            
# =============================================================================
#             if(int(c_tip_n) != int(current_tip)):
#     #check tip availability
#                 if("P300" in str(c_pipette)):
#                     if(tip_counter[0]==96):
#                         protocol.pause('Change P300 tip rack!')
#                         c_pipette.reset_tipracks()
#                         tip_counter[0] = 0
#                     tip_counter[0] = tip_counter[0] + 1
#                         
#                 else:
#                     if(tip_counter[1]==96):
#                         protocol.pause('Change P1000 tip rack!')
#                         c_pipette.reset_tipracks()
#                         tip_counter[1] = 0
#                     tip_counter[1] = tip_counter[1] + 1
#                 
#                 c_pipette.pick_up_tip()
#                 current_tip = int(c_tip_n)
# =============================================================================
        
    
    
    
    
    
    
    
    
    
    
    
    
# =============================================================================
#             if(mix_amt>0):
#                 mix_amt = min(GetSrcVolume(amtList, cmdRow, cur_source_well), 300)
#             
#             #Main Transfers
#             remV = transfer_amt
#             while(remV>0):
#                 #Calculate current transfer amount
#                 cur_transfer = min(300, remV)
#                 if(remV-cur_transfer < 30 and remV-cur_transfer>0):
#                     cur_transfer = cur_transfer/2
#                 remV = remV - cur_transfer
#                 
#                 #update solutions map
#                 amtList = Update_Source(amtList, cmdRow, cur_source_well, cur_transfer)
#                 amtList = Update_Target(amtList, cmdRow, target_well[j], deckMap, cur_transfer)
# 
#                 #calculate aspirate and dispense height
#                 aspH = CalTip_Aspirate(amtList, cmdRow, cur_source_well)
#                 dspH = CalTip_Dispense(amtList, cmdRow, target_well[j])
#                 
#                 #Mix boolean
#                 if(mix_amt==0):
#                     #if no mix
#                     right_pipette.transfer(cur_transfer,
#                                           globals()[source_ware].wells_by_name()[cur_source_well].bottom(aspH),
#                                           globals()[target_ware].wells_by_name()[target_well[j]].bottom(dspH),
#                                           new_tip='never', disposal_volume=0)
#                 else:
#                     #if mix
#                     right_pipette.transfer(cur_transfer,
#                                           globals()[source_ware].wells_by_name()[cur_source_well].bottom(aspH),
#                                           globals()[target_ware].wells_by_name()[target_well[j]].bottom(dspH),
#                                           new_tip='never', mix_before = (3, cur_transfer), disposal_volume=0)
#                 
#                 #blow out on top of the current slot
#                 right_pipette.blow_out(globals()[target_ware].wells_by_name()[target_well[j]].bottom(dspH))
#             
#         #check if tip need to be trashed afterwards
#         if(i == len(cmdList)-1):
#             #if this is the last operation
#             right_pipette.drop_tip()
#         elif(int(cmdRow[6]) != int(cmdList[i+1][6])):
#             #drop if different tip id is detected
#             right_pipette.drop_tip()
# =============================================================================
            


######### SIMULATION ############
from opentrons import simulate
bep = simulate.get_protocol_api('2.10')
bep.home()
run(bep) 
for line in bep.commands():
    print(line)

