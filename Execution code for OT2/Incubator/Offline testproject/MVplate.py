#import
import numpy as np
import pandas as pd
import string
import warnings

warnings.simplefilter(action='ignore', category=Warning)




#################Functions########################
def getstocklist(file):
    res = file.iloc[[0]]
    res = res.dropna(axis = "columns")
    res = res.loc[:, ~res.columns.str.contains('^Unnamed')]
    res.set_index('Drug Name', inplace=True)
    for column in res.columns:
        if isinstance(res[column].iloc[0], str):
            res[column] = res[column].str.replace(",", ".").astype(float)    
    stocklist= res
    return res

def Getwellvol(file):
    res= file.iloc[[3,4]]
    res = res.dropna(axis = "columns")
    res = res.loc[:, ~res.columns.str.contains('^Unnamed')]
    res.set_index('Drug Name', inplace=True)
    res = res.rename(columns={ "AB1": "ul"})
    res = res.rename(index={'Final volume in well (uL)':"TotalVol", "Inoculum volume (uL)":"FillVol"} )
    total_vol = res.loc["TotalVol", "ul"]
    fill_vol = res.loc["FillVol", "ul"]
    Wellinfo = {"total_vol": total_vol, "fill_vol": fill_vol}
    return Wellinfo

def Platenum(file):
    res = file.iloc[[4]]
    res = res.dropna(axis = "columns")
    res = res.loc[:, ~res.columns.str.contains('^Unnamed')]
    res = res.drop(columns=["Drug Name", "AB1"])
    res = res['AB4']
    res = res.values[0]
    return res

def Getplatemap(file):
    res = file.iloc[54:63, : ]
    res.columns = res.iloc[0]
    res = res.drop([54])
    res = res.rename(columns={res.columns[0]: "Well" })
    res = res.dropna(axis = "columns")
    res.set_index("Well", inplace=True)
    
    map_result = []

    for row in range(1, 9):
        # Subset
        curRow = res.iloc[row-1, :].values
        
        # Get info
        well_id = [f"{string.ascii_uppercase[row-1]}{i}" for i in range(1, 13)]
        curRow = pd.DataFrame({'well_id': well_id, 'curRow': curRow})
        
        # Concatenate results
        map_result.append(curRow)
    
    # Concatenate all the DataFrames in the list
    map_result = pd.concat(map_result, ignore_index=True)
    
    
    fin_map = []

    # Parse names
    parsed_names = map_result.iloc[:, 1].apply(lambda x: x.split(' '))
    
    for i in range(len(parsed_names)):
        if map_result.iloc[i, 1] != "0" and map_result.iloc[i, 1] != "":
            if parsed_names[i][0] == "":
                # If both drug name and inoculum is not filled, then it is a blank fill well
                nex_info = ["FILL", "NA", parsed_names[i][1], parsed_names[i][2], "NA"]
            else:
                # If all info is complete OR inoculum not added
                new_names= parsed_names[i][0], parsed_names[i][1], parsed_names[i][2]
                nex_info = [
                    ' '.join(new_names),
                    parsed_names[i][0],  # drug name
                    parsed_names[i][1],  # concentration
                    parsed_names[i][2],  # solvent
                    parsed_names[i][3] if len(parsed_names[i]) > 3 else "NA"  # inoculum
                ]
            # Concatenate well
            fin_map.append(nex_info)
    
    # Create a DataFrame for fin_map
    fin_map_df = pd.DataFrame(fin_map, columns=['solID', 'DrugType', 'DrugConc', 'Solvent', 'Inoc'])
    
    # Remove blanks from map_df
    map_df_filtered = map_result[(map_result.iloc[:, 1] != "") & (map_result.iloc[:, 1] != "0")]
    
    # Concatenate infoz
    final_map = pd.concat([map_df_filtered.reset_index(drop=True), fin_map_df.reset_index(drop=True)], axis=1)
    final_map.columns = ['Well', 'FillID', 'solID', 'DrugType', 'DrugConc', 'Solvent', 'Inoc']
    
    # Expecting dot/comma decimal separator
    if isinstance(final_map['DrugConc'].iloc[0], str):
        final_map['DrugConc'] = final_map['DrugConc'].str.replace(",", ".").astype(float)
    
    # Dropping factor
    final_map = final_map.astype(str)
    
    # Save the result
    res = final_map
    
    # Output the result
    return res

def create_sol_list(plate_map, total_vol_well, inoc_vol, stock_list, n_plate):
    plate_map['solID'] = plate_map['solID'].str.replace(",", ".")
    
    # Get occurrence
    occ = plate_map['solID'].value_counts().reset_index()
    occ.columns = ['solID', 'Occ']
    occ['Occ'] = occ['Occ'] * n_plate
    
    # Combine data frames
    fin_list = plate_map[['solID', 'DrugType', 'DrugConc', 'Solvent']].drop_duplicates()
    fin_list = pd.merge(fin_list, occ, on='solID')
    fin_list = fin_list[fin_list['solID'] != "FILL"]
    fin_list.columns = ['SolID', 'DrugType', 'DrugConc', 'Solvent', 'Occurrence']
    
    # Convert columns to character type
    fin_list = fin_list.astype(str)
    
    # Calculating required dilution volume
    fin_list['Occurrence'] = fin_list['Occurrence'].astype(float)
    fin_list['DrugConc'] = fin_list['DrugConc'].astype(float)
    fin_list = calculate_dil_volume(fin_list, total_vol_well, inoc_vol, stock_list)
    
    return fin_list

def calculate_dil_volume(sol_list, total_vol_well, inoc_vol, stock_list):
    # Calculate initially required amount
    drug_sol_well = total_vol_well - inoc_vol
    sol_list['solAmt'] = sol_list['Occurrence'] * drug_sol_well + 150  # Adds 150 µL excess
    
    # Recalculate amount to adjust with the incoming inoculum
    sol_list['DrugConc'] = sol_list['DrugConc'].astype(float) * total_vol_well / (total_vol_well - inoc_vol)
    
    # Remove no-drug solutions from the list
    sol_list = sol_list[sol_list['DrugType'] != ""]
    
    # Initiate new list
    new_sol_list = pd.DataFrame()
    
    # Iterate through all drug and solvent types
    solvents = sol_list['Solvent'].unique()
    drugs = sol_list['DrugType'].unique()
    
    for solvent in solvents:
        for drug in drugs:
            # Subset the current drug type
            cur_list = sol_list[(sol_list['DrugType'] == drug) & (sol_list['Solvent'] == solvent)]
            
            # Perform following actions only if not null
            if not cur_list.empty:
                # Order according to concentration
                cur_list = cur_list.sort_values(by='DrugConc')
                
                # Add items if additional pre-dilutions are required
                new_cur_list = pd.DataFrame()
                for idx in range(len(cur_list)):
                    new_cur_list = pd.concat([new_cur_list, cur_list.iloc[[idx]]])
                    
                    # Get the current dilution factor
                    if idx == len(cur_list) - 1:
                        conc_hi = stock_list[cur_list['DrugType'].iloc[idx]]
                        cur_dil_fac = conc_hi / cur_list['DrugConc'].iloc[idx]
                
                    else:
                        conc_hi = cur_list['DrugConc'].iloc[idx + 1]
                        cur_dil_fac = conc_hi / cur_list['DrugConc'].iloc[idx]
                    
                    # Check if the current dilution factor is more than 10
                    a= int(cur_list['DrugConc'].iloc[idx] > 0 and cur_dil_fac > 10)
                    
                    if a == 1:
                        iterator = True
                        while cur_dil_fac > 10:
                            if iterator:
                                nex_new_cur_list = cur_list.iloc[[idx]].copy()
                                iterator = False
                            
                            # Update the item list
                            nex_new_cur_list['DrugConc'] = conc_hi / 10
                            nex_new_cur_list['Occurrence'] = 0
                            nex_new_cur_list['SolID'] = f"{nex_new_cur_list['DrugType'].values[0]} {nex_new_cur_list['DrugConc'].values[0]} {nex_new_cur_list['Solvent'].values[0]}"
                            
                            # Concatenate dilution to list
                            new_cur_list = pd.concat([new_cur_list, nex_new_cur_list])
                            
                            # Re-calculate current dilution factor
                            conc_hi = nex_new_cur_list['DrugConc'].values[0]
                            if idx == len(cur_list) - 1:
                                cur_dil_fac = conc_hi / cur_list['DrugConc'].iloc[idx]
                            else:
                                cur_dil_fac = conc_hi / cur_list['DrugConc'].iloc[idx]
            
                cur_list = new_cur_list
                cur_list['solAmt'] = cur_list['solAmt'].astype(float)
                cur_list['DrugConc'] = cur_list['DrugConc'].astype(float)
                cur_list = cur_list.sort_values(by='DrugConc')

                # Check amount needed from above
                needed_from_above = []
                for m in range(len(cur_list)):
                    if m < len(cur_list) - 1:
                        # Usual dilution from pre-diluted stock
                        amt_needed = cur_list['solAmt'].iloc[m] * cur_list['DrugConc'].iloc[m] / cur_list['DrugConc'].iloc[m + 1]
                        
                        # Check if it is lower than the minimum pipette volume
                        b= int(amt_needed < 30 and amt_needed > 0)
                        
                        if b == 1:
                            cur_list['solAmt'].iloc[m] = cur_list['solAmt'].iloc[m] * 30 / amt_needed
                            amt_needed = 30
                        
                        needed_from_above.append(amt_needed)
                        
                        # Add amount to higher concentration
                        cur_list['solAmt'].iloc[m + 1] += amt_needed
                    
                    else:
                        # Calculate amount for initial dilution
                        amt_needed = cur_list['solAmt'].iloc[m] * cur_list['DrugConc'].iloc[m] / stock_list[cur_list['DrugType'].iloc[m]]
                        
                        # Check if it is lower than the minimum pipette volume
                        amt_needed = amt_needed.iloc[0]
                        c = int(amt_needed < 30 and amt_needed > 0)
                        if c == 1:
                            amt_needed = amt_needed
                            cur_list['solAmt'].iloc[m] = cur_list['solAmt'].iloc[m] * 30 / amt_needed
                            amt_needed = 30
                        
                        needed_from_above.append(amt_needed)
                
                needed_from_above = pd.Series(needed_from_above, name='AmtHi')
                needed_from_above.index = cur_list.index 
                nex_item = pd.concat([cur_list, needed_from_above], axis= 1)
                new_sol_list = pd.concat([new_sol_list, nex_item])
    
    # Rename the last column
    new_sol_list = new_sol_list.rename(columns={new_sol_list.columns[-1]: 'AmtHi'})
    
    # Calculate required solvent amount
    new_sol_list['solventAmt'] = new_sol_list['solAmt'] - new_sol_list['AmtHi']
    
    # Check required tube size
    req_tube = ["15_Falcon"] * len(new_sol_list)
    req_tube = pd.Series(req_tube, name='reqTube')
    req_tube.index = new_sol_list.index
    create_null = max(new_sol_list['solAmt']) >= 14 * 1000
    
    # Concatenate Info
    new_sol_list = pd.concat([new_sol_list, req_tube], axis=1)
    
    # Drop factors
    new_sol_list = new_sol_list.astype(str)
    
    if create_null:
        new_sol_list = None
        err_message = "OVER CAPACITY!"
        return new_sol_list, err_message
    
    return new_sol_list

def CreateDilMap(solList, deckMap, stockList):
    solution_map = []
    
    for i, labware in enumerate(deckMap):
        if "Falcon" in deckMap[labware]:
            slots = [f"{chr(65 + row)}{col}" for row in range(3) for col in range(1, 6)]
            current_map = pd.DataFrame({
                'Slot': slots,
                'Fill': "",
                'Labware': labware,
                'solutionType': ""
                })
            solution_map.append(current_map)
        
    solution_map = pd.concat(solution_map, ignore_index = True)
        
        # Assign slots to stock solutions
    stock_labware_names = [labware for labware in deckMap if "stock" in deckMap[labware]]
    stock_indices = solution_map[solution_map['Labware'].isin(stock_labware_names)].index

    if len(stock_indices)< len(stockList):
        raise ValueError("Not enough stock slots available!")
    
    solution_map.loc[stock_indices[:len(stockList.columns)], 'Fill'] = list(stockList.keys())
    solution_map.loc[stock_indices[:len(stockList.columns)], 'solutionType'] = "Stock"
    
    # Filter out stock solutions
    solution_map = solution_map[solution_map['solutionType'] != "Stock"]
    
    # Add address to solutions list
    if len(solList) > len(solution_map):
        raise ValueError("Too many solution types!")
    
    solution_map.loc[:len(solList) - 1, 'Fill'] = solList['SolID'].values
    
    # Select relevant columns and filter out empty fills
    solution_map = solution_map[['Slot', 'Fill', 'Labware']]
    solution_map = solution_map[solution_map['Fill'] != ""]
    
    return solution_map

def Int_CreateCmdList(deckMap, solList, solvent_map, inocMap, dilMap,
                            stockMap, Wellinfo, platemap, PlateNum):
    
    
    return cmdList
#################Main#############################
def Main(file):
    #Read the plate and error handle first
    file = pd.read_excel(file)
    #extract all info and filter out some errors
    try:
        stocklist = getstocklist(file)
    except:
        errMessage = "Input file error - stockList"
        return print(errMessage)
    
    try:
        total_vol, fill_vol = Getwellvol(file)
    except:
        errMessage = "Input file error - Wellinfo"
        return print(errMessage)
    
    try:
        platemap = Getplatemap(file)
    except:
        errMessage = "Input file error - Platemap"
    
    try:
        PlateNum = Platenum(file)
    except:
        errMessage = "Input File error - Plate number"
    
    try:
        solList = create_sol_list(platemap, total_vol, fill_vol, stocklist, PlateNum)
    except:
        errMessage = "Input file error - Platemap"
   ###############get Solution list and Dilution scheme#######################
   ##############Load Labwares#######################
    if errMessage == "":
       deckMap = ['96-well_D', '96-well_E', '96-well_F', '96-well_A', '96-well_B', '96-well_C', 'tip', '15_Falcon_spare',
                  '15_Falcon_main', '15ml_Falcon_stock', 'Solvent', 'TRASH']
       deckMap = {f'labware_{i+1}': deckMap[i] for i in range(len(deckMap))}

       coords = [1, 1]
       solvent_map= []
       solvents = platemap['Solvent'].unique()

       for solvent in solvents:
           next_item = [f'{chr(64 + coords[0])}{coords[1]}', solvent]
           solvent_map.append(next_item)
           #update fill coordinates
           coords[1] += 1
           if coords[1] > 3:
               # Reset the second coordinate
               coords[1] = 1
               # Increment the first coordinate
               coords[0] += 1
           
       #stock
       #iniciate map
       coords = [1, 1]
       print(coords)
       stockMap= []
       # Iterate through all items in stockList
       for i, stock_item in enumerate(stocklist):
           next_item = [f'{chr(64 + coords[0])}{coords[1]}', stock_item]
           stockMap.append(next_item)
           print(i)
           # Update fill coordinates
           print(coords)
           coords[2 - 1] += 1
           print(coords)
           if coords[2 - 1] > 5:  # as 15 mL Falcon tube racks
               coords[2 - 1] = 1
               coords[1 - 1] += 1

    ######################assign slot for dilution solutions################
    try:
        dilMap = CreateDilMap(solList, deckMap, stocklist)
    except:
        errMessage = "Can not make dil map"
       
    ################Create command list###################
    if errMessage == "":
        #initiate map
        coords = [1, 1]
        #start list for innocs
        inocMap = []
        inocs = platemap['Inoc'].unique()
        inocs = inocs[inocs != 'NA']
        
        #find all strains that are given. And run through them
        for i in range(len(inocs)):
            # Generate the well identifier (e.g., A1, A2, ...)
            well_identifier = f"{string.ascii_uppercase[coords[0]]}{coords[1]}"
            # Create the next item with the well identifier and the corresponding inoculum value
            nextItem = [well_identifier, str(inocs[i])]
            # Append the next item to inocMap
            inocMap.append(nextItem)
            
            # Update coordinates
            coords[1] += 1
            if coords[1] > 5:  # If column index exceeds 5, move to the next row
                coords[1] = 1
                coords[0] += 1
    
#testing
file = "C:\\Users\\jornb\\Documents\\GitHub\\ot2\\Execution code for OT2\\Incubator\\Test User inputs\\MV_InputTemplate.xlsx"
file = pd.read_excel(file)
stocklist = getstocklist(file)
PlateNum = Platenum(file)
Wellinfo = Getwellvol(file)
platemap= Getplatemap(file)
solList = create_sol_list(platemap, Wellinfo['total_vol'], Wellinfo['fill_vol'], stocklist, PlateNum)


#Testing part
#load labwares for test
deckMap = ['96-well_D', '96-well_E', '96-well_F', '96-well_A', '96-well_B', '96-well_C', 'tip', '15_Falcon_spare',
           '15_Falcon_main', '15ml_Falcon_stock', 'Solvent', 'TRASH']
deckMap = {f'labware_{i+1}': deckMap[i] for i in range(len(deckMap))}

coords = [1, 1]
solvent_map= []
solvents = platemap['Solvent'].unique()

for solvent in solvents:
    next_item = [f'{chr(64 + coords[0])}{coords[1]}', solvent]
    solvent_map.append(next_item)
    #update fill coordinates
    coords[1] += 1
    if coords[1] > 3:
        # Reset the second coordinate
        coords[1] = 1
        # Increment the first coordinate
        coords[0] += 1
    
#stock
#iniciate map
coords = [1, 1]
stockMap= []
# Iterate through all items in stockList
for i, stock_item in enumerate(stocklist):
    next_item = [f'{chr(64 + coords[0])}{coords[1]}', stock_item]
    stockMap.append(next_item)
    # Update fill coordinates
    coords[2 - 1] += 1
    if coords[2 - 1] > 5:  # as 15 mL Falcon tube racks
        coords[2 - 1] = 1
        coords[1 - 1] += 1

dilMap = CreateDilMap(solList, deckMap, stocklist)

#initiate map
coords = [1, 1]
#start list for innocs
inocMap = []
inocs = platemap['Inoc'].unique()
inocs = inocs[inocs != 'NA']

for i in range(len(inocs)):
    # Generate the well identifier (e.g., A1, A2, ...)
    well_identifier = f"{string.ascii_uppercase[coords[0]]}{coords[1]}"
    # Create the next item with the well identifier and the corresponding inoculum value
    nextItem = [well_identifier, str(inocs[i])]
    # Append the next item to inocMap
    inocMap.append(nextItem)
    
    # Update coordinates
    coords[1] += 1
    if coords[1] > 5:  # If column index exceeds 5, move to the next row
        coords[1] = 1
        coords[0] += 1
        
cmdList = Int_CreateCmdList(deckMap, solList, solvent_map, inocMap, dilMap,
                            stockMap, Wellinfo, platemap, PlateNum)
