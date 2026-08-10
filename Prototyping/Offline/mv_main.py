"""
Python port of the R main() function + Int_CreateCmdList().
Produces:
  - a CSV command list for the robot (equivalent to cmdList_output's
    '>CommandLines' section)
  - an xlsx "RobotHandler" amount/deck-layout file (equivalent to
    usercmd_output / cmdList_output combined)
"""
import sys
from collections import OrderedDict
import pandas as pd
from openpyxl import Workbook

from mv_source import (
    MVError, get_stock_list, get_well_vols, get_n_plate, get_plate_map,
    create_sol_list, create_dil_map, cmd_init_dist, cmd_hi_drug,
    cmd_serial_dil, cmd_drug_sol_dist, cmd_fill_outer, cmd_separate_long,
    cal_sol_amt, cal_stock_amt, make_stock_map, make_solvent_map,
    make_inoc_map, cal_dil_tubes, cal_deck_adjustment,
    convert_amtlist_mv_to_mc, cal_amtlist_excess, convert_amtlist_mc_to_mv,
    CMD_COLS,
)

DECK_MAP = OrderedDict([
    ('labware_1', '96-well_D'), ('labware_2', '96-well_E'), ('labware_3', '96-well_F'),
    ('labware_4', '96-well_A'), ('labware_5', '96-well_B'), ('labware_6', '96-well_C'),
    ('labware_7', 'tip'), ('labware_8', '15_Falcon_main'), ('labware_9', '15_Falcon_spare'),
    ('labware_10', '15ml_Falcon_stock'), ('labware_11', 'Solvent'), ('labware_12', 'TRASH'),
])


def int_create_cmd_list(deck_map, sol_list, solvent_map, inoc_map, dil_map,
                         stock_map, well_info, plate_map, n_plate):
    cmd = cmd_init_dist(deck_map, sol_list, solvent_map, dil_map)
    cmd = cmd_hi_drug(cmd, sol_list, stock_map, deck_map, dil_map)
    cmd = cmd_serial_dil(cmd, sol_list, dil_map)
    cmd = cmd_drug_sol_dist(cmd, dil_map, plate_map, deck_map, well_info, n_plate)
    cmd = cmd_fill_outer(plate_map, deck_map, solvent_map, well_info, cmd, n_plate)
    return cmd


def run(file_path):
    stock_list = get_stock_list(file_path)
    well_info = get_well_vols(file_path)
    plate_map = get_plate_map(file_path)
    n_plate = get_n_plate(file_path)

    sol_list = create_sol_list(plate_map, well_info['TotalVol'], well_info['FillVol'],
                                stock_list, n_plate)

    solvent_map = make_solvent_map(plate_map)
    stock_map = make_stock_map(DECK_MAP, stock_list)
    inoc_map = make_inoc_map(plate_map)

    dil_map = create_dil_map(sol_list, DECK_MAP, stock_list)

    cmd_list = int_create_cmd_list(DECK_MAP, sol_list, solvent_map, inoc_map,
                                    dil_map, stock_map, well_info, plate_map, n_plate)
    cmd_list = cmd_separate_long(cmd_list)
    cmd_list = cmd_list.reset_index(drop=True)

    all_amt = pd.concat([
        cal_sol_amt(DECK_MAP, solvent_map, cmd_list),
        cal_stock_amt(sol_list, stock_list, stock_map, DECK_MAP),
    ], ignore_index=True)

    dil_tubes = cal_dil_tubes(dil_map)
    fin_deck = cal_deck_adjustment(cmd_list, DECK_MAP, dil_tubes, n_plate)

    all_amt2 = convert_amtlist_mv_to_mc(all_amt)
    deck_map2 = pd.DataFrame({'Labware': list(DECK_MAP.keys()), 'Desc': list(DECK_MAP.values())})

    cmd_list, adjusted_tubes = cal_amtlist_excess(all_amt2, cmd_list, deck_map2)
    all_amt = convert_amtlist_mc_to_mv(adjusted_tubes)

    return {
        'cmd_list': cmd_list,
        'all_amt': all_amt,
        'dil_tubes': dil_tubes,
        'fin_deck': fin_deck,
        'n_plate': n_plate,
    }


def _fmt(v):
    """Mimic R's as.character(numeric): integer-valued numbers print
    without a decimal point, others print without a trailing '.0' and
    without excess float noise."""
    if isinstance(v, float):
        if v == int(v) and abs(v) < 1e15:
            return str(int(v))
        # R's as.character(numeric) uses ~15 significant digits
        s = f"{v:.15g}"
        return s
    return v


def _flat_platemap_rows(deck_map, fin_deck):
    """Reproduces R main()'s flattening of the 8x3 fin_deck grid into
    12 (labware_N, description) rows sorted by N -- used in the CSV's
    '>PlateMap' section."""
    numbers = []
    descs = []
    for i in range(0, 8, 2):
        numbers.extend(fin_deck[i])
        descs.extend(fin_deck[i + 1])
    pairs = sorted(zip(numbers, descs), key=lambda x: int(x[0]))
    return [(f"labware_{n}", d) for n, d in pairs]


def write_outputs(result, out_csv, out_xlsx):
    cmd_list = result['cmd_list']
    all_amt = result['all_amt']
    dil_tubes = result['dil_tubes']
    fin_deck = result['fin_deck']
    platemap_rows = _flat_platemap_rows(DECK_MAP, fin_deck)

    # --- CSV: combined Amount List / Command Lines / Plate Map, matching
    # the server's cmdList_output layout exactly ---
    with open(out_csv, 'w', newline='') as f:
        import csv
        w = csv.writer(f)
        w.writerow(CMD_COLS)
        w.writerow(['>Amount List'])
        for _, r in all_amt.iterrows():
            w.writerow([r['Labware'], r['Slot'], r['Name'], '', _fmt(r['RequiredAmount']), '', '', ''])
        w.writerow(['>CommandLines'])
        for _, r in cmd_list.iterrows():
            w.writerow([_fmt(r[c]) for c in CMD_COLS])
        w.writerow(['>PlateMap'])
        for labware, desc in platemap_rows:
            w.writerow([labware, desc, '', '', '', '', '', ''])

    # --- xlsx: RobotHandler workbook (single sheet) ---
    wb = Workbook()
    ws = wb.active
    ws.title = "Sheet1"
    ws.append(list(all_amt.columns))
    for row in all_amt.itertuples(index=False):
        ws.append([_fmt(v) for v in row])
    for row in dil_tubes.itertuples(index=False):
        ws.append([_fmt(v) for v in row])
    ws.append(['>>> OT2 DECK MAP <<<'])
    for i in range(0, 8, 2):
        ws.append(list(fin_deck[i]))
        ws.append(list(fin_deck[i + 1]))
    wb.save(out_xlsx)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python mv_main.py <input.xlsx> [out_prefix]")
        sys.exit(1)
    in_path = sys.argv[1]
    prefix = sys.argv[2] if len(sys.argv) > 2 else 'MV_output'
    try:
        result = run(in_path)
    except MVError as e:
        print(f"ERROR: {e}")
        sys.exit(1)
    write_outputs(result, f"{prefix}_commands.csv", f"{prefix}_RobotHandler.xlsx")
    print("Done.")
    print(f"  {prefix}_commands.csv  ({len(result['cmd_list'])} command lines)")
    print(f"  {prefix}_RobotHandler.xlsx")
