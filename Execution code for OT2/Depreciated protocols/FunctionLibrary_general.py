################################
# Library for direct operations (on-opentrons)

####### CUSTOM LIBRARY #########
def ReadCSV_Dat(file_name):
    #save all read info into the variable: command_list
    content_list = np.empty(9)
    with open(file_name, 'r') as file:
        cmdCSV = csv.reader(file, delimiter=',')
        for cmdRow in cmdCSV:
            content_list = np.vstack([content_list, cmdRow])
    
    #Find starting point of amount list and command list
    indices = []
    for a in range(len(content_list)):
        if(">" in content_list[a][0]):
            indices.append(a)
    
    #get amount list
    amt_list = content_list[indices[0]+1:indices[1]]
    amt_list = [x[[0, 1, 2, 4]] for x in amt_list]
    
    #get command list
    cmd_list = content_list[indices[1]+1:indices[2]]
    
    #get input deck map
    inp_deckMap = content_list[indices[2]+1:]
    
    #parse out deck location and fills
    deck_loc = [x[0] for x in inp_deckMap]
    fill = [x[1] for x in inp_deckMap]
    deck_map = {}
    for i in range(len(deck_loc)):
        if('96' in fill[i] or 'eep' in fill[i]):
            if('eep' in fill[i]):
                fill[i] = "nest_96_wellplate_2ml_deep"
            else:
                fill[i] = "nest_96_wellplate_200ul_flat"
        elif('15' in fill[i]):
            fill[i] = "opentrons_15_tuberack_falcon_15ml_conical"
        elif('50' in fill[i] or "olvent" in fill[i] or "nno" in fill[i] or "SOLVENT" in fill[i]):
            fill[i] = "opentrons_6_tuberack_falcon_50ml_conical"
        elif('dorf' in fill[i] or 'tock' in fill[i] or "1.5" in fill[i]):
            fill[i] = "opentrons_24_tuberack_nest_1.5ml_snapcap"
        elif('tip' in fill[i] or 'Tip' in fill[i]):
            if("1000" in fill[i]):
                fill[i] = "opentrons_96_tiprack_1000ul"
            else:
                fill[i] = "opentrons_96_tiprack_300ul"
        
        deck_map[deck_loc[i]] = fill[i]
        
    return amt_list, cmd_list, deck_map
def Update_Source(amt_list, cmd_line, source_well, current_transAmt):
    #get tube location
    tube_loc = [(x[0]==cmd_line[0] and x[1]==source_well) for x in amt_list]
    tube_loc = [i for i, x in enumerate(tube_loc) if x]
    
    #get source amount after dispensed
    amt_list[tube_loc[0]][3] = float(amt_list[tube_loc[0]][3]) - current_transAmt
    
    return(amt_list)
def Update_Target(amt_list, cmd_line, target_well, deck_map, current_transAmt):
    #get tube location
    tube_loc = [(x[0]==cmd_line[2] and x[1]==target_well) for x in amt_list]
    tube_loc = [i for i, x in enumerate(tube_loc) if x]
    
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
    
    #if not 96 well plate
    if('96-well' not in tube_type):
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
        elif("1.5" in tube_type):
            #Tube Dimensions - Eppendorf
            h_bot = 37.8-20 #mm
            r = 8.7/2 #mm
            minH = 2
            stab = 5 #mm
        else:
            #deep well dimensions
            h_bot = 0
            r = 8.5/2 #mm
            minH = 2 #mm
            stab = 4 #mm
        
        #calculate height
        Vmax_bot = pi*r**2*h_bot/3
        
        if(src_amt>Vmax_bot):
            h_tip = h_bot + (src_amt - Vmax_bot)/(pi*r**2)
        else:
            h_tip = ((3*src_amt*h_bot**2)/(pi*r**2))**(1/3)
    
    #if source is a 96-well plate
    else:
        #assign well dimensions
        r = 6.45/2 #mm
        minH = 1.5 #mm
        
        h_tip = src_amt/(pi*r**2)
        
    #add stab distance; place minimum height into place
    h_tip = max(h_tip-5, minH)
    
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
    
    #if source is a 96-well plate
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