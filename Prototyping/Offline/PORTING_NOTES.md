# Porting notes: MVsourceFunctions.R -> Python

## Status: verified byte-for-byte match against the real server output

You sent me `CommandList_..._01_B_J.csv` and `RobotHandler_..._01_B_J.xlsx`
from the actual server, generated from the same `MV_InputTemplate.xlsx`.
I diffed my output against both, row by row / cell by cell:

- **CSV: identical**, all 68 rows.
- **RobotHandler xlsx: identical**, all 16 rows.

Two bugs got fixed to get there, both worth knowing about:

### 1. Border/no-drug well detection (the missing water fills)
R's `read_xlsx()` trims leading/trailing whitespace from cell strings by
default (`trim_ws = TRUE`). openpyxl doesn't do this automatically. Your
border wells' cached formula value is `" 0 MED_A "` (leading space, from
`CONCATENATE(drugname, " ", conc, " ", medium, " ", strain)` with an empty
`drugname`) — with the leading space intact, R's FILL-well check
(`parsed_names[[i]][1]=="0"`) silently never matched, and no
"Filling outer wells with WATER" commands ever got generated.

Fix: strip the cell string before parsing (`get_plate_map()` in
`mv_source.py`), matching R's actual read behavior. This was confirmed by
comparing against your real server CSV, which does contain the outer-well
fill commands — 12 of them, matching exactly once the fix was in.

### 2. Cascading tip IDs after splitting long well-lists
`Cmd_SeparateLong()` in R splits any command targeting more than 8 wells
into <=8-well chunks, each getting a fresh tip. After splitting row `i`, the
R code also shifts the `TipID` of every *subsequent* row by however many
extra chunks were just inserted (`cmd_list[i:nrow,7] <- ... + d_tip - 1`).
My first pass missed that cascade, so tip numbers after the first
multi-plate outer-well-fill command were off by a few. Fixed in
`cmd_separate_long()` in `mv_source.py`.

Everything else — dilution math, serial dilution ordering, volume
rounding/tube-splitting, deck layout — matched on the first try.

## Files
- `mv_source.py` — all the individual ported functions.
- `mv_main.py` — orchestration (`run()` + `write_outputs()`), mirrors R's
  `main()`. Run directly:
  ```
  python mv_main.py path/to/YourPlate.xlsx output_prefix
  ```
  Produces `<prefix>_commands.csv` (matches the server's combined
  `>Amount List` / `>CommandLines` / `>PlateMap` CSV format exactly) and
  `<prefix>_RobotHandler.xlsx` (single sheet, matches the server's
  RobotHandler format exactly).
- `example_output_commands.csv` / `example_output_RobotHandler.xlsx` — the
  verified-identical output for your `MV_InputTemplate.xlsx`.

## Requirements
```
pip install pandas openpyxl numpy
```
No R, no server, no network access needed to run it.

## Caveat
This has been verified against exactly one example plate (4 drugs, 3
concentration levels each, 2 plates, 1 medium, no pre-existing solvent
stock, no tube-overflow splitting triggered). The dilution-scheme code in
particular (`calculate_dil_volume` / `CalculateDilVolume`) has several
branches this example doesn't exercise — e.g. what happens when a required
dilution factor is so large it needs more than one intermediate
pre-dilution step, or when a solvent/stock tube would exceed the 45 mL /
14 mL fill limit and a second tube gets allocated
(`cal_amtlist_excess` / `cal_amtList_Excess`). I ported those branches
faithfully from the R source, but haven't tested them against a real
server output. If you run this against a plate that exercises one of
those paths, send me that server output too so I can check it.
