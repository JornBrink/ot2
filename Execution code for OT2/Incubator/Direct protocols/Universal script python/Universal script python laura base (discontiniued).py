#INPUTS------------
fileName = "Halving_CommandList.csv"

#IMPORTS---------
import csv
import os
import numpy as np
from math import pi
from opentrons import protocol_api, types

#METADATA----------
metadata = {
    'protocolName': 'Universal python script',
    'author': 'Sebastian <sebastian.tandar@gmail.com> Jorn Brink <brinkj@vuw.leidenuniv.nl',
    'description': 'Universal script for OT2 van Hasselt lab',
    'apiLevel': '2.12'
}

#ADDITIONAL FUNCTIONS--------
def ReadCSV_input(file_name):
    content_list = np.empty(10)
    with open(file_name, 'r') as file:
        try:
            cmdCSV = csv.reader(file, delimiter=',')
            for cmdRow in cmdCSV:
                content_list = np.vstack([content_list, cmdRow])
        except:
            cmdCSV = csv.reader(file, delimiter=';')
            for cmdRow in cmdCSV:
                content_list = np.vstack([content_list, cmdRow])
    
    #Find starting point of amount list and command list
    indices = []
    for a in range(len(content_list)):
        if(">" in content_list[a][0]):
            indices.append(a)
    
    #separate command input info
    solution_list = []
    for a in content_list[indices[0]+1:indices[1]]:
        solution_list.append(a[0:3])
    
    #get command list
    cmdList = content_list[indices[1]+1:indices[2]]
    
    deck_map = []
    for a in content_list[indices[2]+1:len(content_list)]:
        deck_map.append(a[0:2])
        
    return(solution_list, cmdList, deck_map)

def translate_labwareLibrary(string_identifier):
    if("384" in string_identifier):
        #labware_name = "greiner_384_wellplate_115ul"
        labware_name = "corning_384_wellplate_112ul_flat"

    elif("48" in string_identifier):
        labware_name = "greinerbioone677102_48_wellplate_1000ul"
        
    elif("96" in string_identifier):
        if("dilution" in string_identifier or "deep" in string_identifier):
            #labware_name = "custom_96_deep_well_2000ul"
            labware_name = "nest_96_wellplate_2ml_deep"
        else:
            labware_name = "nest_96_wellplate_200ul_flat"
            
    elif("tiprack" in string_identifier or "tip" in string_identifier or "p3" in string_identifier or "p1" in string_identifier):
        if("1000" in string_identifier):
            labware_name = "opentrons_96_tiprack_1000ul"
        elif("300m" in string_identifier):
            labware_name = "opentrons_96_tiprack_300ul"
        else:
            labware_name = "opentrons_96_tiprack_300ul"
            
    elif("solvent" in string_identifier):
        labware_name = "opentrons_6_tuberack_falcon_50ml_conical"
        
    elif("eservoir" in string_identifier):
        labware_name = "nest_12_reservoir_15ml"
        
    elif("alcon" in string_identifier):
        if("15" in string_identifier):
            labware_name = "opentrons_15_tuberack_falcon_15ml_conical"
        else:
            labware_name = "opentrons_6_tuberack_falcon_50ml_conical"
            
    else:
        labware_name = "opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap"
    
    return labware_name

def get_LabwareCaller(deck_num):
    caller_id = "labware_"+str(int(deck_num))
    return caller_id

def cal_transferSpeed(min_trans_amt):
    if(min_trans_amt < 300):
        trans_speed = min(min_trans_amt / 1.5, 150) # upper limit of 150 ul/s
    else:
        trans_speed = min(min_trans_amt / 1.5, 250) # upper limit of 250 ul/s for higher volume transfers
    return(trans_speed)

def cal_aspH(ware_name, transfer_v, deck_name, slot_name, amt_list):
    
     # A | Get array index
    locationID = []
    for item in amt_list:
        locationID.append(str(item[0])+"_"+item[1])
        
    # B | Get initial source volume
    location_index = locationID.index((str(deck_name)+"_"+slot_name))
    remaining_v = float(amt_list[location_index][2]) 
    
    # C | Calculate source volume after transfer
    rem_v = remaining_v - transfer_v
    
    # D | Calculate required tip height
    # IF other tubes: assume tubular with conical end
    #get dimensions
    if(("50" in ware_name, "15" in ware_name, "1,5" in ware_name) and ("eservoir" not in ware_name or "eep" not in ware_name)):
        if("50" in ware_name):
            h_bot = 15.88 #mm
            r = 28.14/2 #mm
            minH = 2 #mm
            stab = 7 #mm
        elif("15" in ware_name):
            h_bot = 23.36 #mm
            r = 15.62/2 #mm
            minH = 2 #mm
            stab = 5 #mm
        else:
            #Tube Dimensions - Eppendorf
            h_bot = 37.8-20 #mm
            r = 8.7/2 #mm
            minH = 2
            stab = 3 #mm

        #calculate required height
        Vmax_bot = pi*r**2*h_bot/3 #volume of bottom cone
        
        if(rem_v>Vmax_bot):
            if(rem_v > (Vmax_bot + 50) and ("1.5" in ware_name)):
                h_tip = 17 # hard-code location for eppendorfs
            else:
                h_tip = h_bot + (rem_v - Vmax_bot)/(pi*r**2)
        else:
            if("1.5" in ware_name):
                h_tip = 5 # hard-code location for eppendorfs
            else:
                h_tip = ((3*rem_v*h_bot**2)/(pi*r**2))**(1/3)
                
    elif("96" in ware_name and ("eep" not in ware_name or "dilution" not in ware_name)):
        r = 6.45/2 #mm
        minH = 2 #mm
        h_tip = src_amt/(pi*r**2) 
        
    #if source is a nest reservoir
    elif( "eservoir" in ware_name):
        h_tip = src_amt /8.2/73.2 #volume with a mm stap
        stab = 10
        minH = 2

    else:
    #deep well dimensions
        h_bot = 0
        r = 8.5/2 #mm
        minH = 2 #mm
        stab = 4 #mm

        
        #add stab distance; place minimum height into place
    h_tip = max(h_tip-stab, minH)
    
    return(h_tip)

def cal_dspH(ware_name, transfer_v, deck_name, slot_name, amt_list):
     # A | Get array index
    locationID = []
    for item in amt_list:
        locationID.append(str(item[0])+"_"+item[1])
        
    # B | Get initial source volume
    try:
        location_index = locationID.index((str(deck_name)+"_"+slot_name))
        remaining_v = float(amt_list[location_index][2]) 
    except:
        #if location not yet in the list
        remaining_v = 0
        
    # C | Calculate target volume after transfer
    rem_v = remaining_v + transfer_v
    
    # D | Calculate required tip height
    # IF deep well plate : assume tubular
    if("eep" in ware_name):
        h_tip = rem_v / pi / ((7.82/2)**2) + 2 # 2 mm hover
        h_tip = max(h_tip, 3)
    
    # IF 96 or 384-well plate
    elif("96" in ware_name):
        h_tip = 10 # fixed hover at 10 mm

    elif("384" in ware_name):
        h_tip = 6 # fixed hover at 6 mm

    elif("48" in ware_name):
        h_tip = 8 # fixed hover at 8 mm
    
    # IF other tubes: assume tubular with conical end
    # get dimensions
    else:
        if("50" in ware_name):
            h_bot = 15.88 #mm
            r = 28.14/2 #mm
            minH = 2 #mm
            hover = 7 #mm
        elif("15" in ware_name):
            h_bot = 23.36 #mm
            r = 15.62/2 #mm
            minH = 2 #mm
            hover = 5 #mm
        elif("1.5" in ware_name):
            #Tube Dimensions - Eppendorf
            h_bot = 37.8-20 #mm
            r = 8.7/2 #mm
            minH = 2
            hover = 3 #mm

        #calculate required height
        Vmax_bot = pi*r**2*h_bot/3 #volume of bottom cone
        
        if(rem_v>Vmax_bot):
            h_tip = h_bot + (rem_v - Vmax_bot)/(pi*r**2)
        else:
            h_tip = ((3*rem_v*h_bot**2)/(pi*r**2))**(1/3)
        
        #add stab distance; place minimum height into place
        h_tip = max(h_tip+hover, minH)
    
    return(h_tip)

def update_amtList(amt_list, deck_name, slot_name, trans_amt, current_operation):
    # A | Get array index
    locationID = []
    for item in amt_list:
        locationID.append(str(item[0])+"_"+item[1])
    
    # B | Modify target
    if current_operation == "dispense":
        # update for dispense
        try:
            #if location ID already available in the amount list
            location_index = locationID.index((str(deck_name)+"_"+slot_name))
            amt_list[location_index][2] = float(amt_list[location_index][2]) + trans_amt
        except:
            #if slot is newly filled
            amt_list.append([str(deck_name), slot_name, trans_amt])
    else:
        # update for aspirate
        location_index = locationID.index((str(deck_name)+"_"+slot_name))
        amt_list[location_index][2] = float(amt_list[location_index][2]) - trans_amt
     
    return amt_list
    
############# MAIN #############
def run(protocol: protocol_api.ProtocolContext):
    #global cmdList, deckMap, amtList
    try:
        os.chdir("C://Users//jornb//Documents//GitHub//ot2new//Execution code for OT2//Incubator//Direct protocols//Universal script python")
        
    except:
        os.chdir('/var/lib/jupyter/notebooks/User Inputs')
        
    amtList, cmdList, deckMap = ReadCSV_input(fileName)
    ############ LOAD LABWARES ############
    tipLocs_300s = []
    tipLocs_300m = []
    tipLocs_1000 = []
    labwareCaller = {}
    for i in range(12):
        #perform only if name not null
        if(deckMap[i][1]!="" and deckMap[i][1]!="trash"):
            #find labware name
            current_labware_name = translate_labwareLibrary(deckMap[i][1])
            caller_id = 'labware_' + str(i+1)
            
            if("300m" in current_labware_name):
                labwareCaller[caller_id] = protocol.load_labware("opentrons_96_tiprack_300ul", i+1)
            else:
                labwareCaller[caller_id] = protocol.load_labware(current_labware_name, i+1)

            #if labware is a tip rack, assign number to tip location(s)
            if("tiprack" in current_labware_name):
                if("1000" in current_labware_name):
                    tipLocs_1000.append(labwareCaller[caller_id])
                elif("300m" in current_labware_name):
                    tipLocs_300m.append(labwareCaller[caller_id])
                else:
                    tipLocs_300s.append(labwareCaller[caller_id])
                    
    Pipette = [current_line[8] for current_line in cmdList]    
    #load pipettes
        #P300 single-channel
    right_pipette = protocol.load_instrument('p300_single_gen2', 'right', tip_racks=tipLocs_300s)
        #p1000 single-channel
    if("p1000" in Pipette or "P1000" in Pipette or "p1" in Pipette or "P1" in Pipette):
        left_pipette = protocol.load_instrument('p1000_single_gen2', 'left', tip_racks=tipLocs_1000)
    else:
        left_pipette = protocol.load_instrument('p300_multi_gen2', 'left', tip_racks=tipLocs_300m)
    
        #combine
    pipette_caller = {"p1000" : left_pipette, "p300" : right_pipette}

    ############### INITIATE TIP COUNTER ############
    tip_counter = [0, 0] # p300s or p300m or p1000 depending on what is initialized
    current_tip = 0
    
    ############### EXECUTE ###############
    #parse address and amount
    SourceLabware = [current_line[0] for current_line in cmdList]
    SourceSlot = [current_line[1] for current_line in cmdList]
    TargetLabware = [current_line[2] for current_line in cmdList]
    TargetSlot = [current_line[3] for current_line in cmdList]
    TransAmt = [current_line[4] for current_line in cmdList]
    MixAmt = [current_line[5] for current_line in cmdList]
    TipID = [current_line[6] for current_line in cmdList]
    Pipette = [current_line[8] for current_line in cmdList]
    
    #perform operation per-aspirate group 
    #fuck fuck fuck why is Asp_set a thing...... why not jsut have a progressbar........
    aspirate_groups = [int(current_line[7]) for current_line in cmdList]
    aspirate_groups2 = []
    progressMax = len(aspirate_groups)
    for x in aspirate_groups:
        if x not in aspirate_groups2:
            aspirate_groups2.append(x)
 
    for i in range(len(aspirate_groups2)):
        aspirate_group2 = cmdList[i]
        print("Progress\t: " + str(int(round(i/progressMax*100))) + "%")
        print(aspirate_group2)
        
        #get current aspirate group
        asp_group = aspirate_groups2[i]
        if i != len(aspirate_groups2)-1:
            nex_asp_group = aspirate_groups2[i+1]
        
        # A | get address
        current_set = [i for i, j in enumerate(aspirate_groups) if int(j) == asp_group]
        
        next_set = [i for i, j in enumerate(aspirate_groups) if j == nex_asp_group]
        
        c_source_deck = SourceLabware[current_set[0]]
        c_source_slot = SourceSlot[current_set[0]]
        
        c_target_deck = [TargetLabware[i] for i in current_set]
        c_target_slot = [TargetSlot[i] for i in current_set]

        c_pipette = pipette_caller[Pipette[current_set[0]]]
        c_amt = [TransAmt[i] for i in current_set]
        c_MixAmt = float(MixAmt[current_set[0]])
        if("P300" in str(c_pipette)):
            c_mix = min(float(MixAmt[current_set[0]]), 300)
        else:
            c_mix = min(float(MixAmt[current_set[0]]), 800)
            
        c_tip_n = TipID[current_set[0]]
        tip_next = TipID[next_set[0]]
        
        # B | tip pick up/no decision
        if(int(c_tip_n) != int(current_tip)):
            #check tip availability
            if("P300" in str(c_pipette)):
                if(tip_counter[0]==96):
                    protocol.pause('Change P300 tip rack!')
                    c_pipette.reset_tipracks()
                    tip_counter[0] = 0
                tip_counter[0] = tip_counter[0] + 1
                    
            else:
                if(tip_counter[1]==96):
                    protocol.pause('Change P1000 tip rack!')
                    c_pipette.reset_tipracks()
                    tip_counter[1] = 0
                tip_counter[1] = tip_counter[1] + 1
            
            c_pipette.pick_up_tip()
            current_tip = int(c_tip_n)
            
        
        # C | separate liquid transfer operations
        if(len(c_target_slot)==1):
            if(len(str(c_target_slot[0]).split(", "))==1):
                operation = 1
            else:
                operation = 2
        else:
            operation = 3
        
        # D | Main Transfer operation
        if(operation==1):
            #    setup multiple transfers when needed
            transferV = float(c_amt[0])
            if("P300" in str(c_pipette)):
                max_trans = 300
            else:
                max_trans = 1000
            
            while(transferV>0):
                if(transferV < max_trans):
                    # case 1: volume well within max. amount
                    current_transfer = transferV
                    transferV = 0
                elif(transferV < 2*max_trans):
                    # case 2: volume exceed max. amount; but below 2x max. amount
                    current_transfer = transferV / 2
                    transferV = transferV/2
                else:
                    # case 3: volume exceeded twice max. amount
                    current_transfer = max_trans
                    transferV = transferV - max_trans
                
                # calculate tip aspirate/dispense height
                current_aspH = cal_aspH(str(labwareCaller[get_LabwareCaller(c_source_deck)]), 
                                        current_transfer, c_source_deck, c_source_slot, amtList)
                current_dspH = cal_dspH(str(labwareCaller[get_LabwareCaller(c_target_deck[0])]), 
                                        current_transfer, c_target_deck[0], c_target_slot[0], amtList)
                
                # adjust aspirate/dispense speed
                current_aspSpeed = cal_transferSpeed(current_transfer)
                c_pipette.flow_rate.aspirate=current_aspSpeed

                # adjust dispense speed for 384 well plate
                if("384" not in str(labwareCaller[get_LabwareCaller(c_target_deck[0])])):
                    c_pipette.flow_rate.dispense=max(current_aspSpeed, 75) # max. 75 dispense speed for common labwares
                else:
                    c_pipette.flow_rate.dispense=max(current_aspSpeed/2, 25) #half speed for 384 well-plate; min. of 25
          
                # perform liquid transfer)
                if(c_mix > 0):
                    c_pipette.transfer(current_transfer, 
                                       labwareCaller[get_LabwareCaller(c_source_deck)].wells_by_name()[c_source_slot].bottom(current_aspH),
                                       labwareCaller[get_LabwareCaller(c_target_deck[0])].wells_by_name()[c_target_slot[0]].bottom(current_dspH),
                                       new_tip='never',  mix_before=(3, c_mix))
                else:
                    c_pipette.transfer(current_transfer, 
                                       labwareCaller[get_LabwareCaller(c_source_deck)].wells_by_name()[c_source_slot].bottom(current_aspH),
                                       labwareCaller[get_LabwareCaller(c_target_deck[0])].wells_by_name()[c_target_slot[0]].bottom(current_dspH),
                                       new_tip='never')
		
        		#   adjust blow out speed
                if("384" not in str(labwareCaller[get_LabwareCaller(c_target_deck[0])])):
                    c_pipette.flow_rate.blow_out = 250
               	else:
                    c_pipette.flow_rate.blow_out = 100

                c_pipette.blow_out(labwareCaller[get_LabwareCaller(c_target_deck[0])].wells_by_name()[c_target_slot[0]].bottom(current_dspH+3))
                
	        	# touch tip only if target is a deep-well plate
                if("384" not in str(labwareCaller[get_LabwareCaller(c_target_deck[0])])):
                    c_pipette.touch_tip(labwareCaller[get_LabwareCaller(c_target_deck[0])].wells_by_name()[c_target_slot[0]], radius=0.8)
                else:
                    c_pipette.touch_tip(labwareCaller[get_LabwareCaller(c_target_deck[0])].wells_by_name()[c_target_slot[0]],
                                        radius=0.45, speed=15)
                
                # update amount list
                amtList = update_amtList(amtList, c_source_deck, c_source_slot, current_transfer, "aspirate")
                amtList = update_amtList(amtList, c_target_deck[0], c_target_slot[0], current_transfer, "dispense")
                
        else:
            # Operation 2 and 3 : one to many; manual
            #adjusting for removal of automatic dispensing option
            if(operation == 2):
                c_target_slot = str(c_target_slot[0]).split(", ")
                if(len(c_amt)==1):
                    c_amt = [c_amt[0] for a in c_target_slot]
                    c_target_deck = [c_target_deck[0] for a in c_target_slot]
                    
            
            # calculate tip aspirate height
            current_aspH = cal_aspH(str(labwareCaller[get_LabwareCaller(c_source_deck)]), 
                                             sum([float(a) for a in c_amt]), 
                                             c_source_deck, c_source_slot, amtList)
            
            # adjust aspirate speed
            c_pipette.flow_rate.aspirate=cal_transferSpeed(sum([float(a) for a in c_amt]))
            
            #   aspirate
            c_pipette.aspirate(sum([float(a) for a in c_amt]),
                               labwareCaller[get_LabwareCaller(c_source_deck)].wells_by_name()[c_source_slot].bottom(current_aspH))
            
            #   update source amount list
            amtList = update_amtList(amtList, c_source_deck, c_source_slot, sum([float(a) for a in c_amt]), 'aspirate')
            
           
            #   dispense
            for j in range(len(c_target_deck)):
                #adjust dispense speed
                # adjust dispense speed for 384 well plate
                if("384" not in str(labwareCaller[get_LabwareCaller(c_target_deck[0])])):
                    c_pipette.flow_rate.dispense=max(cal_transferSpeed(float(c_amt[j])), 75) # lower limit of 75 for common labwares
                else:
                    c_pipette.flow_rate.dispense=max(cal_transferSpeed(float(c_amt[j]))/2, 25) # half-speed; min dispense speed of 25 for 384-well plate

                #dispense
                current_dspH = cal_dspH(str(labwareCaller[get_LabwareCaller(int(c_target_deck[j]))]), 
                                        float(c_amt[j]), c_target_deck[j], c_target_slot[j], amtList)
                # transfer amount
                c_pipette.dispense(float(c_amt[j]),
                                   labwareCaller[get_LabwareCaller(int(c_target_deck[j]))].wells_by_name()[c_target_slot[j]].bottom(current_dspH))
                
                # touch tip
                if(j < (len(c_target_deck)-1)):
                    if("384" not in str(labwareCaller[get_LabwareCaller(c_target_deck[j])])):
                        c_pipette.touch_tip(labwareCaller[get_LabwareCaller(c_target_deck[j])].wells_by_name()[c_target_slot[j]], radius=0.8)
                    else:
                        c_pipette.touch_tip(labwareCaller[get_LabwareCaller(c_target_deck[j])].wells_by_name()[c_target_slot[j]],
                                            radius=0.45, speed=15)
                        
                #   update target amount list
                amtList = update_amtList(amtList, c_target_deck[j], c_target_slot[j], float(c_amt[j]), 'dispense')
            
	            #   adjust blow out speed
                if("384" not in str(labwareCaller[get_LabwareCaller(c_target_deck[-1])])):
                    c_pipette.flow_rate.blow_out = 250
                else:
                    c_pipette.flow_rate.blow_out = 100

            #   blow out at last target
            c_pipette.blow_out(labwareCaller[get_LabwareCaller(c_target_deck[-1])].wells_by_name()[c_target_slot[-1]].bottom(current_dspH+3))
            
    	    #touch tip
            if("384" not in str(labwareCaller[get_LabwareCaller(c_target_deck[-1])])):
                c_pipette.touch_tip(labwareCaller[get_LabwareCaller(c_target_deck[-1])].wells_by_name()[c_target_slot[-1]], radius=0.8)
            else:
                c_pipette.touch_tip(labwareCaller[get_LabwareCaller(c_target_deck[-1])].wells_by_name()[c_target_slot[-1]],
                                        radius=0.5, speed=15)
                    
        #drop tip decision
        if(int(tip_next) != int(current_tip) or (i == len(aspirate_groups2)-1)):
            c_pipette.drop_tip(protocol.fixed_trash['A1'].top().move(types.Point(10, 5, 12)))


######### SIMULATION ############
from opentrons import simulate
bep = simulate.get_protocol_api('2.10')
bep.home()
run(bep) 
for line in bep.commands():
    print(line)
