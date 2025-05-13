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
            
        os.chdir(directscriptpath)
        
        #opening the directscript
        with open('Drugdilution96.py') as f:
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
                       "'description':'Opentrons Flex custom script''User customized drugdilution on OT2'}\n" + "\n")
            file.write("requirements = {'robotType': 'Flex', 'apiLevel': '2.19'}")
            
            for asd in lines:
                file.write(asd)
                
            if(simulation == "1"):
                file.write("\n" + "##########Simulation##########" + "\n" "from opentrons import simulate" + "\n" +
                           "bep = simulate.get_protocol_api('2.19'), robot_type = 'Flex'" + "\n" + 
                           "bep.home()" + "\n" + "run(bep)" + "\n" +
                           "for line in bep.commands():" + "\n"+"\t"+"print(line)")
        return
        
    elif "Drugditlution384.py" in directscript:
        os.chdir(directscriptpath)
        
        #opening the directscript
        with open('Drugditlution384.py') as f:
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
            file.write('brand =' + "\'" + brand + "\'" + "\n" + "\n")
            file.write("touch_tips = 'Yes'" + "\n" + "\n")
            file.write("#METADATA----------" + "\n" + 
                       'metadata = {'+"\n"+"\t"+
                       "\'"+ 'protocolName'"\'"+":"+  "\'" + protocolname + "\'" +","+"\n"+"\t"+
                       "'author':'Sebastian <sebastian.tandar@gmail.com>''Jorn <jornbrink@kpnmail.nl>'," + "\n"+"\t"+
                       "'description':'Opentrons Flex custom script''User customized drugdilution on OT2'}\n" + "\n")
            file.write("requirements = {'robotType': 'Flex', 'apiLevel': '2.19'}")
            
            for asd in lines:
                file.write(asd)
                
            if(simulation == "1"):
                file.write("\n" + "##########Simulation##########" + "\n" "from opentrons import simulate" + "\n" +
                           "bep = simulate.get_protocol_api('2.19'), robot_type = 'Flex'" + "\n" + 
                           "bep.home()" + "\n" + "run(bep)" + "\n" +
                           "for line in bep.commands():" + "\n"+"\t"+"print(line)")
        return