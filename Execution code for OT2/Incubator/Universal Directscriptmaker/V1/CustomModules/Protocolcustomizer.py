import FreeSimpleGUI as sg
import os

def Protocolcustomizer(experimentname, simulation, fileName, pc, brand, protocolname, activerobot, directscript):
    #this should take the directscript <- selected in the window
    #start getting pathing
    if simulation == "1":
        basepath = os.getcwd() #this will be the same as the main executable
        newpathDS = basepath + "//Newdirectscripts"
        if "qPCR" in directscript or "Drugdilution96flex" in directscript:
            directscriptpath = os.getcwd() +  '//Directscripts//Flex'
        else:
            directscriptpath = os.getcwd() +  '//Directscripts//OT2'
        
    else:
        userpath = os.path.expanduser("~")
        directscriptpath = userpath + "//Desktop//Directscripts//" + pc
        newpathDS = userpath + "//Desktop//New Direct scripts"
    
    if "96wells_qPCR.py" in directscript:
        os.chdir(directscriptpath)
        
        #opening the directscript
        with open('96wells_qPCR.py') as f:
            lines=f.readlines()
        
        #change working directory to the new script spot for making the new script
        os.chdir(newpathDS)
        
        try:
            fh = open(experimentname, 'r+')
        except:
            fh= open(experimentname, 'w+')
        
        with open (experimentname, 'w+') as file:
            file.write("# This protocol is made for " + activerobot + "\n")
            file.write("fileName = '" + fileName + ".csv'" + "\n" + "\n")
            file.write("pc = '" + pc + "'" + "\n" + "\n")
            file.write("brand = 'Greiner'" + "\n" + "\n")
            file.write("touch_tips = 'Yes'" + "\n" + "\n")
            file.write("#METADATA----------" + "\n" + 
                       'metadata = {'+"\n"+"\t"+
                       "\'"+ 'protocolName'"\'"+":"+  "\'" + protocolname + "\'" +","+"\n"+"\t"+
                       "'author':'Sebastian <sebastian.tandar@gmail.com>''Jorn <jornbrink@kpnmail.nl>'," + "\n"+"\t"+
                       "'description':'Opentrons Flex custom script''User customized qPCR'}\n" + "\n")
            file.write("requirements = {'robotType': 'Flex', 'apiLevel': '2.19'}")
            
            for asd in lines:
                file.write(asd)
                
            if(simulation == "1"):
                file.write("\n" + "##########Simulation##########" + "\n" "from opentrons import simulate" + "\n" +
                           "bep = simulate.get_protocol_api('2.19'), robot_type = 'Flex'" + "\n" + 
                           "bep.home()" + "\n" + "run(bep)" + "\n" +
                           "for line in bep.commands():" + "\n"+"\t"+"print(line)")
        return
    
    elif "Drugdilution96flex.py" in directscript:
            os.chdir(directscriptpath)
            
            #opening the directscript
            with open('Drugdilution96flex.py') as f:
                lines=f.readlines()
            
            #change working directory to the new script spot for making the new script
            os.chdir(newpathDS)
            
            try:
                fh = open(experimentname, 'r+')
            except:
                fh= open(experimentname, 'w+')
            
            with open (experimentname, 'w+') as file:
                file.write("# This protocol is made for " + activerobot + "\n")
                file.write("fileName = '" + fileName + ".csv'" + "\n" + "\n")
                file.write("pc = '" + pc + "'" + "\n" + "\n")
                file.write("touch_tips = 'Yes'" + "\n" + "\n")
                file.write("#METADATA----------" + "\n" + 
                           'metadata = {'+"\n"+"\t"+
                           "\'"+ 'protocolName'"\'"+":"+  "\'" + protocolname + "\'" +","+"\n"+"\t"+
                           "'author':'Sebastian <sebastian.tandar@gmail.com>''Jorn <jornbrink@kpnmail.nl>'," + "\n"+"\t"+
                           "'description':'Opentrons Flex custom script''User customized drugdilution on Flex'}\n" + "\n")
                file.write("requirements = {'robotType': 'Flex', 'apiLevel': '2.19'}")
                
                for asd in lines:
                    file.write(asd)
                    
                if(simulation == "1"):
                    file.write("\n" + "##########Simulation##########" + "\n" "from opentrons import simulate" + "\n" +
                               "bep = simulate.get_protocol_api('2.19'), robot_type = 'Flex'" + "\n" + 
                               "bep.home()" + "\n" + "run(bep)" + "\n" +
                               "for line in bep.commands():" + "\n"+"\t"+"print(line)")
            return
        
    elif "Drugdilution96.py" in directscript:
        
        with open(Truename, 'w+') as file:
                    file.write("#" + 'This protocol is made for'+ " " + fileName + "\n")
                    file.write('fileName =' + "\'" + fileName  + '.csv'+ "\'" "\n" + "\n")
                    file.write('pc =' + "\'" + pc + "\'" + "\n" + "\n")
                    file.write('touch_tips =' + "\'" + "No" + "\'" + "\n" + "\n")
                    file.write('#METADATA----------' "\n" +
                                'metadata = {'+"\n"+"\t"+
                                    "\'"+ 'protocolName'"\'"+":"+  "\'" + protocolname + "\'" +","+"\n"+"\t"+
                                    "\'"+'author'"\'"+":" + "\'" +'Sebastian <sebastian.tandar@gmail.com>' +"\'" +"\'"+ 'Jorn <jornbrink@kpnmail.nl>' + "\'"+"," +"\n"+"\t"+
                                    "\'"+'description'"\'"+":" + "\'" +'96 wells plate MIC with p300 possibility'+"\'"+ "\'"+'User customized'+"\'"+","+ "\n"+"\t"+
                                    "\'"+'apiLevel'"\'"+":"+"\'" +'2.15'+"\'"+ "\n"+'}\n')
                    
                    #actually puts the script into the new file
                    for asd in lines:
                        file.write(asd)
                        
                    if(simulation == "1"):
                        file.write("\n" + "##########Simulation##########" + "\n" "from opentrons import simulate" + "\n" +
                                   "bep = simulate.get_protocol_api('2.15')" + "\n" + 
                                   "bep.home()" + "\n" + "run(bep)" + "\n" + "amtList, cmdList, deckMap = ReadCSV_dat(filename)" + "\n"+
                                   "for line in bep.commands():" + "\n"+"    print(line)")
        
    elif "Drugditlution384.py" in directscript:
        with open(Truename, 'w+') as file:
                    file.write("#" + 'This protocol is made for'+ " " + fileName + "\n")
                    file.write('fileName =' + "\'" + fileName  + '.csv'+ "\'" "\n" + "\n")
                    file.write('pc =' + "\'" +pc + "\'" + "\n" + "\n")
                    file.write('brand =' + "\'" + brand + "\'" + "\n" + "\n")
                    file.write('touch_tips =' + "\'" + "No" + "\'" + "\n" + "\n")
                    file.write('#METADATA----------' "\n" +
                                'metadata = {'+"\n"+"\t"+
                                    "\'"+ 'protocolName'"\'"+":"+  "\'" + protocolname + "\'" +","+"\n"+"\t"+
                                    "\'"+'author'"\'"+":" + "\'" +'Sebastian <sebastian.tandar@gmail.com>' +"\'" +"\'"+ 'Jorn <jornbrink@kpnmail.nl>' + "\'"+"," +"\n"+"\t"+
                                    "\'"+'description'"\'"+":" + "\'" +'96 wells plate MIC with p300 possibility'+"\'"+ "\'"+'User customized'+"\'"+","+ "\n"+"\t"+
                                    "\'"+'apiLevel'"\'"+":"+"\'" +'2.15'+"\'"+ "\n"+'}\n')
                    
                    #actually puts the script into the new file
                    for asd in lines:
                        file.write(asd)
                        
                    if(simulation == "1"):
                        file.write("\n" + "##########Simulation##########" + "\n" "from opentrons import simulate" + "\n" +
                                   "bep = simulate.get_protocol_api('2.15')" + "\n" + 
                                   "bep.home()" + "\n" + "run(bep)" + "\n" + "amtList, cmdList, deckMap = ReadCSV_input(fileName)" + "\n"+
                                   "for line in bep.commands():" + "\n"+"    print(line)")
                    else:
                        print ("Simulation mode inactive")
        
    else:
        sg.popup("It seems that you have not selected anything?", keep_on_top=True)
    return

directscriptname = 'asdf_adsf_dsaf.py'
simulation ="1"
cmdfilename = "wupwup.csv"
pc = "Jorn"
protname = "qpcr"
robotname= "Wall-E"
test = Protocolcustomizer(directscriptname, simulation, cmdfilename, pc, "brand", protname, robotname,  "qPCR.py")

        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
    
# =============================================================================
#     with open(Truename, 'w+') as file:
#             file.write("#" + 'This protocol is made for'+ " " + activeOT2 + "\n")
#             file.write('fileName =' + "\'" + file_name_meta  + '.csv'+ "\'" "\n" + "\n")
#             file.write('pc =' + "\'" +active_pc + "\'" + "\n" + "\n")
#             if(values['384wy'] == True):
#                 file.write('brand =' + "\'" + brand + "\'" + "\n" + "\n")
#             else:
#                 print("")
#             file.write('touch_tips =' + "\'" + touch_tips + "\'" + "\n" + "\n")
#             file.write('#METADATA----------' "\n" +
#                         'metadata = {'+"\n"+"\t"+
#                             "\'"+ 'protocolName'"\'"+":"+  "\'" + Direct_protocol_name + "\'" +","+"\n"+"\t"+
#                             "\'"+'author'"\'"+":" + "\'" +'Sebastian <sebastian.tandar@gmail.com>' +"\'" +"\'"+ 'Jorn <jornbrink@kpnmail.nl>' + "\'"+"," +"\n"+"\t"+
#                             "\'"+'description'"\'"+":" + "\'" +'96 wells plate MIC with p300 possibility'+"\'"+ "\'"+'User customized'+"\'"+","+ "\n"+"\t"+
#                             "\'"+'apiLevel'"\'"+":"+"\'" +'2.15'+"\'"+ "\n"+'}\n')
#             
#             #actually puts the script into the new file
#             for asd in lines:
#                 file.write(asd)
#                 
#             if(simulation == "1" and values['384wn'] == True):
#                 file.write("\n" + "##########Simulation##########" + "\n" "from opentrons import simulate" + "\n" +
#                            "bep = simulate.get_protocol_api('2.15')" + "\n" + 
#                            "bep.home()" + "\n" + "run(bep)" + "\n" + "amtList, cmdList, deckMap = ReadCSV_dat(filename)" + "\n"+
#                            "for line in bep.commands():" + "\n"+"    print(line)")
#             elif(simulation == "1" and values['384wy'] == True):
#                 file.write("\n" + "##########Simulation##########" + "\n" "from opentrons import simulate" + "\n" +
#                            "bep = simulate.get_protocol_api('2.15')" + "\n" + 
#                            "bep.home()" + "\n" + "run(bep)" + "\n" + "amtList, cmdList, deckMap = ReadCSV_input(fileName)" + "\n"+
#                            "for line in bep.commands():" + "\n"+"    print(line)")
#             else:
#                 print ("Simulation mode inactive")
# =============================================================================
