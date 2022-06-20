#spare: exec(compile(open("/var/lib/jupyter/notebooks/MainExec.py", "rb").read(), "SeparatedCommaned.py", 'exec'))
###### HOW TO USE #####
# 2. Click the "refresh kernel" button (it's beside the stop button)
# 3. Click ">| Run" button

# 4. Put in your file name (include the csv); then press enter. quotation marks are not needed

# 5. Its going to ask you what pipettes are attached; you can say either "### or p###"
#   > So p1000 is "1000 or p1000"
#   > So p300 is "300 or p300"
#   > NOTE THE MULICHANNEL PIPETTE IS ONLY ON THE LEFT (FOR NOW ATLEASED) AND IS p300m OR 300m 

# 6. Wait for the simulation to complete. This step will check if an error is going to occur.
#    > This will take ~3 minutes

# 7. If everything went well, you will see: "SIMULATION COMPLETE", and will ask your permission to continue the run
#    > To continue run, fill "Y", then press ENTER
#    > as final confirmation, pressENTER again
#    > If otherwise an error was found, you can choose to continue the run anyway, or cancel it (fill "N", then press ENTER)

#exec(compile(open("C:/Users/jornb/OT2 left/Development/MainExec_for_MIC_test.py", "rb").read(), "SeparatedCommaned.py", 'exec'))
exec(compile(open("/var/lib/jupyter/notebooks/MainExec_SkipRows.py", "rb").read(), "SeparatedCommaned.py", 'exec'))


#exec(compile(open("/var/lib/jupyter/notebooks/MainExec.py", "rb").read(), "SeparatedCommaned.py", 'exec'))
