import PySimpleGUI as sg
import os
import subprocess
import json
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
from pathlib import Path

#BIG EXPLANATION: Somehow do i have save the input from the main window but the childwindow(network driver) is not yet saved (i have no clue how i did it)
#I have the feeling window.close is the reason but i am not entirely sure
x = "NA"
str(x)

def Mainwindow():
    listofusers = os.listdir('C://Users')
    global x
    #print(listofusers)
    if ("cvhLa" in listofusers):
            #print("nonsimulation mode")
            simulation = "0"
    else:
            simulation = "1"
            #print("simulation mode active")
    
    # create the layout with buttons and text
    if (simulation == "1"):
        layout = [
            [sg.Button("Make command list")],
            [sg.Button("Refresh")],
            [sg.Text("Please provide information about the OT2 run you want to do")],
            [sg.Text('Select a file', size=(18,1)), sg.FileBrowse(file_types= (('CSV Files', '*.csv'),))],                      #Browse
            [sg.Text('Or use the one you just send'), sg.Text(str(x), key='-importfilename-')],
            [sg.Radio("Selected", "group 3", key="Miep1", default = True), sg.Radio("Made", "group 3", key= "Miep2")],
            [sg.Text('Experiment Name', size=(18,1)), sg.InputText('')],                                                        #values0
            [sg.Text('Your Name', size=(18, 1)), sg.InputText('')],                                                             #values1
            [sg.Text('Date (yymmdd)', size=(18, 1)), sg.InputText('')],                                                         #values2
            [sg.Text('Which OT2 do you want to use?')],                       
            [sg.Radio('OT2L', "group 1"), sg.Radio('OT2R', "group 1")],                                                         #Values3&4
            [sg.Text("What pc is it running on?")],
            [sg.Radio('Jorn', "group 2"), 
             sg.Radio('Sebastian', "group 2"), sg.Radio('OT', "group 2")],                                                      #Values[5/6/7]
            [sg.Button("Save"),sg.Button("Send", disabled=True), sg.Button("Close")]
        ]
    else:
        layout = [
            [sg.Button("Make command list")],
            [sg.Button("Refresh")],
            [sg.Text("Please provide information about the OT2 run you want to do")],
            [sg.Text('Select a file', size=(18,1)), sg.FileBrowse(file_types= (('CSV Files', '*.csv'),))],  #Browse
            [sg.Text('Or use the one you just send'), sg.Text(str(x), key='-importfilename-')],
            [sg.Radio("Selected", "group 3", key="Miep1", default = True), sg.Radio("Made", "group 3", key= "Miep2")],            
            [sg.Text('Experiment Name', size=(18,1)), sg.InputText('')],                                    #values0
            [sg.Text('Your Name', size=(18, 1)), sg.InputText('')],                                         #values1
            [sg.Text('Date (yymmdd)', size=(18, 1)), sg.InputText('')],                                     #values2
            [sg.Text('Which OT2 do you want to use?')],                       
            [sg.Radio('OT2L', "group 1"), sg.Radio('OT2R', "group 1")],                                     #Values3&4
            [sg.Text("What pc is it running on?")],
            [sg.Radio('Jorn', "group 2", disabled = True), 
             sg.Radio('Sebastian', "group 2", disabled = True), sg.Radio('OT', "group 2", default = True)], #Values5
            [sg.Button("Save"),sg.Button("Send", disabled=True), sg.Button("Close")],
            ]
    return sg.Window("Opentron direct protocol maker", layout, finalize = True), simulation

def Webinteraction():
    layout = [
        [sg.Text("Please provide all information below")],
        [sg.Text("Choose your file: "), sg.FileBrowse()],                                                   #values['Browse']
        [sg.Text("Platemap PMID"), sg.InputText('')],                                                       #values[0]
        [sg.Text("Your name (First Last)"), sg.InputText('')],                                              #values[1]
        [sg.Text("Experiment Name"), sg.InputText('')],                                                     #values[2]
        [sg.Text("Experiment number"), sg.InputText('')],                                                   #values[3]
        [sg.Text("What type of experiment are you going to do?")],
        [sg.Radio("Checkerboard", "group1"), 
         sg.Radio("Multiplate MIC", "group1"), 
         sg.Radio("384 well plate", "group1"), 
         sg.Radio("M9MixR", "group1")],                                                                     #values4/5/6/7
        [sg.Text("Do you want to fill outer wells in robot? (384 plate only)")],
        [sg.Radio("Yes", "group2"), sg.Radio("No", "group2")],                                              #values8/9
        [sg.Button("Save User Inputs"), sg.Button("Send to Server", disabled = True) , sg.Button("Close")]
        ]
    return sg.Window("Webdriver", layout, finalize= True)

#File sending function
def Filesending(fullpath, pmid_plate, Firstname, Lastname, Experiment_name, Experiment_num, simulation):
    #it searches per id most of the time if possible
    fileinput = driver.find_element(By.ID, "file").send_keys(fullpath)
    Plate_Map_ID = driver.find_element(By.ID, "pmid").send_keys(values[0])
    Firstname_file = driver.find_element(By.ID, "f_name").send_keys(Firstname)
    Lastname_file = driver.find_element(By.ID, "l_name").send_keys(Lastname)
    Experiment_name_file = driver.find_element(By.ID, "exp_name").send_keys(Experiment_name)
    Experiment_num_file = driver.find_element(By.ID, "exp_num").send_keys(Experiment_num)
    #these sleeptimers are so it doesnt just try to download or click something while this is not possible or might give some problems
    time.sleep(2)
    confirmupload = driver.find_element(By.ID, "do").click()
    time.sleep(3)
    textFromDiv = driver.find_element(By.XPATH, "//div[@class='shiny-text-output shiny-bound-output']").text
    file_name = "CommandList_" + textFromDiv + ".csv"
    
    if(simulation == "1"):
        path_to_cmd = "C://Users//jornb//Documents//GitHub//ot2new//Execution code for OT2//Incubator//OT2DirectprotocolCustomizer//Webdriver//Firefox download test" + '//' + file_name
    else:
        path_to_cmd = "C://Users//cvhLa//Onedrive//Desktop//User input (for direct)" + '//' + file_name
    
    check=os.path.isfile(path_to_cmd)
    
    #This is a recommendation --> it checks if the file already is present, with the input from a few variables before.
    if(check == True):
        #If the filename already exists this might lead to problems with the further processing of the file. Also forces people to think about their names (when using the app)
        sg.Popup("The file name is already taken please change this", keep_on_top=True)
        driver.close()
    
    else:
        #if not it will download the files
        DownloadRobot = driver.find_element(By.ID, "d_OT2").click()
        time.sleep(3)
        DownloadSetup = driver.find_element(By.ID, "guide").click()
        #checks another time if the command file exists.
        time.sleep(3)
        check2 = os.path.isfile(path_to_cmd)
        RSP = "Robothandler_" + textFromDiv + ".xlsx"
        if(simulation == "1"):
            path_to_RSP = "C://Users//jornb//Documents//GitHub//ot2new//Execution code for OT2//Incubator//OT2DirectprotocolCustomizer//Webdriver//Firefox download test" + '//' + RSP
        else:
            path_to_RSP = "C://Users//cvhLa//Onedrive//Desktop//User input (for direct)" + '//' + RSP
        check3 = os.path.isfile(path_to_RSP)
        if(check2 == False):
            DownloadRobot = driver.find_element(By.ID, "d_OT2").click()
        elif(check3 == False):
            DownloadSetup = driver.find_element(By.ID, "guide").click()
        else:
            if(simulation == "1"):
                new_pathRSP = "C://Users//jornb//Downloads//" + RSP
            else:
                new_pathRSP = "C://Users//cvhLa//Downloads//" + RSP
        os.replace(path_to_RSP, new_pathRSP)
        sg.Popup("Files should be downloaded(click OK when ready to close browser and continue)", keep_on_top = True)
        global x
        x = "CommandList_" + textFromDiv
        driver.close()
    return

def Filesending384(fullpath, fillingrobot, notfillingrobot, pmid_plate, Firstname, Lastname, Experiment_name, Experiment_num, simulation):
    fileinput = driver.find_element(By.ID, "file").send_keys(fullpath)
    if (fillingrobot == True):
        element = driver.find_element(By.ID, "fillOuter")
        element.click()
    else:
        print("no outerwell will be filled by OT") 
    
    fileinput = driver.find_element(By.ID, "file").send_keys(fullpath)
    Plate_Map_ID = driver.find_element(By.ID, "pmid").send_keys(values[0])
    Firstname_file = driver.find_element(By.ID, "f_name").send_keys(Firstname)
    Lastname_file = driver.find_element(By.ID, "l_name").send_keys(Lastname)
    Experiment_name_file = driver.find_element(By.ID, "exp_name").send_keys(Experiment_name)
    Experiment_num_file = driver.find_element(By.ID, "exp_num").send_keys(Experiment_num)
    #these sleeptimers are so it doesnt just try to download or click something while this is not possible or might give some problems
    time.sleep(2)
    confirmupload = driver.find_element(By.ID, "do").click()
    time.sleep(3)
    textFromDiv = driver.find_element(By.XPATH, "//div[@class='shiny-text-output shiny-bound-output']").text
    file_name = "CommandList_" + textFromDiv + ".csv"
    
    if(simulation == "1"):
        path_to_cmd = "C://Users//jornb//Documents//GitHub//ot2new//Execution code for OT2//Incubator//OT2DirectprotocolCustomizer//Webdriver//Firefox download test" + '//' + file_name
    else:
        path_to_cmd = "C://Users//cvhLa//Onedrive//Desktop//User input (for direct)" + '//' + file_name
    
    check=os.path.isfile(path_to_cmd)
    
    #This is a recommendation --> it checks if the file already is present, with the input from a few variables before.
    if(check == True):
        #If the filename already exists this might lead to problems with the further processing of the file. Also forces people to think about their names (when using the app)
        sg.Popup("The file name is already taken please change this", keep_on_top=True)
        driver.close()
    
    else:
        #if not it will download the files
        DownloadRobot = driver.find_element(By.ID, "d_OT2").click()
        time.sleep(3)
        DownloadSetup = driver.find_element(By.ID, "guide").click()
        #checks another time if the command file exists.
        time.sleep(3)
        check2 = os.path.isfile(path_to_cmd)
        RSP = "Robothandler_" + textFromDiv + ".xlsx"
        if(simulation == "1"):
            path_to_RSP = "C://Users//jornb//Documents//GitHub//ot2new//Execution code for OT2//Incubator//OT2DirectprotocolCustomizer//Webdriver//Firefox download test" + '//' + RSP
        else:
            path_to_RSP = "C://Users//cvhLa//Onedrive//Desktop//User input (for direct)" + '//' + RSP
        check3 = os.path.isfile(path_to_RSP)
        if(check2 == False):
            DownloadRobot = driver.find_element(By.ID, "d_OT2").click()
        elif(check3 == False):
            DownloadSetup = driver.find_element(By.ID, "guide").click()
        else:
            if(simulation == "1"):
                new_pathRSP = "C://Users//jornb//Downloads//" + RSP
            else:
                new_pathRSP = "C://Users//cvhLa//Downloads//" + RSP
        os.replace(path_to_RSP, new_pathRSP)
        sg.Popup("Files should be downloaded(click OK when ready to close browser and continue)", keep_on_top = True)
        global x
        x = "CommandList_" + textFromDiv
        driver.close()
    return


#activate first window
window1, window2 = Mainwindow(), None

    # create popup that is to inform user
def popup_connecting():
    clicked = sg.PopupOKCancel("This is going to take a bit (might not respond while sending file)\n",
             "Please press OK to continue")
    if (clicked =="OK"):
        return
    else:
       window.close() 
    return

listofusers = os.listdir('C://Users')
values = []
if ("cvhLa" in listofusers):
    simulation = "0"
else:
    simulation = "1"

#Needs to store the Directscript into memory for later use
if(simulation == "1"):    
    os.chdir("C://Users//jornb//Documents//GitHub//ot2new//Execution code for OT2//Incubator//OT2DirectprotocolCustomizer//V5 with webdriver")
else:
    os.chdir("C://Users//cvhLa//OneDrive//Desktop//Direct Protocols")
lines = []
with open('Directscript.py') as f:
    lines = f.readlines()

#FUNCTIONS----------

def getIPs():
    # load data
    if (simulation == "1"):
        f = open('C://Users//jornb//AppData//Roaming//Opentrons//discovery.json')
    else:
        f = open('C://Users//cvhLa//AppData//Roaming//Opentrons//discovery.json')
    json_data = json.load(f)['robots']
    
    # initiate loop
    robot_ip_list = {}
    names = []
    addresses = []
    
    # get IP address for each robot
    for i in range(len(json_data)):
        # subset json data for current robot
        current_data = json_data[i]
        
        # extract relevant info; append
        robot_ip_list[current_data['name']] = current_data['addresses'][0]['ip']
        names.append(current_data['name'])
        addresses.append(current_data['addresses'][0]['ip'])
    
    return robot_ip_list
        
#creates loop that activates the tracking of events and values in the gui
while True:
    window, event, values = sg.read_all_windows()
    
    #Stops everything when user uses the button cancel or closes the window
    if event =="Close" or event == sg.WIN_CLOSED:
        window.close()
        if window == window2:
            window2 == None
        elif window == window1:
            break
        #small little problem --> this will break everything and stop it from reacting but its the best i can do for now
        
    if event == 'Refresh':
            x = str(x)
            window['-importfilename-'].update(str(x))
            
    #If user wants to make a commandlist open new window
    if event == 'Make command list':
        window2 = Webinteraction()
    
    #If user sets save the file is found and prepared for making the script
    if event == 'Save':
        #put filename = into the script
        if(simulation == "1"): #and values[5] == True):
            os.chdir("C://Users//jornb//Documents//GitHub//ot2new//Execution code for OT2//Incubator//OT2DirectprotocolCustomizer//V5 with webdriver//New Direct scripts")
        elif(simulation == "1" and values[6] == True): #change This @sebastian
            os.chdir("C://Users//jornb//Documents//GitHub//ot2new//Execution code for OT2//Incubator//OT2DirectprotocolCustomizer//V5 with webdriver//New Direct scripts")
        else:
            os.chdir("C://Users//cvhLa//OneDrive//Desktop//New Direct scripts")
        print(values)
        if(values[0] == "" or values[2]== "" or values[3]== "" or values['Browse'] == "" and 'Miep1' == True):
            sg.Popup("Fill all fields and options", keep_on_top = True)
            break #tempuary measure to break
        else:
            Direct_protocol_name = values[2]+values[1]+values[0]
            Truename = (Direct_protocol_name+ '.py')
            try:
                fh = open(Truename, 'r+')
            except FileNotFoundError:
                fh = open(Truename, 'w+')
            
            #pull the files appart to make sure that we get the expected values for the metadata
            if('Miep 1' == True):
                file_name_meta = values['Browse']
                file_name_meta= Path(file_name_meta)
                file_name_meta = file_name_meta.name
                file_name_meta = file_name_meta.split(".")
                file_name_meta = file_name_meta[0]
            else:
                file_name_meta = x
                
            #creates the option to create the possiblity for simulations (does not uncomment the simulation underneath the directscript)
            if(values[5] == True and simulation == "1" ):
                active_pc ="Jorn"
            elif(values[6] == True and simulation == "1"):
                active_pc = "Sebastian"
            else:
                active_pc = "OT"
                
            # For the metadata of the script added
            with open(Truename, 'w+') as file:
                    file.write('fileName =' + "\'" + file_name_meta  + '.csv'+ "\'" "\n" + "\n")
                    file.write('pc =' + "\'" +active_pc + "\'" + "\n" + "\n")
                    file.write('#METADATA----------' "\n" +
                                'metadata = {'+"\n"+"\t"+
                                    "\'"+ 'protocolName'"\'"+":"+  "\'" + Direct_protocol_name + "\'" +","+"\n"+"\t"+
                                    "\'"+'author'"\'"+":" + "\'" +'Sebastian <sebastian.tandar@gmail.com>' +"\'" +"\'"+ 'Jorn <jornbrink@kpnmail.nl>' + "\'"+"," +"\n"+"\t"+
                                    "\'"+'description'"\'"+":" + "\'" +'96 wells plate MIC with p300 possibility'+"\'"+ "\'"+'Usercustomized'+"\'"+","+ "\n"+"\t"+
                                    "\'"+'apiLevel'"\'"+":"+"\'" +'2.12'+"\'"+ "\n"+'}\n')
                    #actually puts the script into the new file
                    for asd in lines:
                        file.write(asd)
                        
                    if(simulation == "1"):
                        file.write("\n" + "##########Simulation##########" + "\n" "from opentrons import simulate" +
                                   "bep = simulate.get_protocol_api('2.12')" + "\n" + 
                                   "bep.home()" + "\n" + "run(bep)")
                    else:
                        print ("Simulation mode inactive")
                    
           #enables the send button
            window['Send'].update(disabled=False)
        
            # check robot IP
            robot_ip = getIPs()
    
    if event == 'Send':
        #when value 4 is true then the OT2L is selected and the script tries to send the csv to the jupyter
        if(values[3] == True):
            try:
                popup_connecting()
                fileName_direc = file_name_meta  + '.csv'+ '\'' + " "
                path_to_file = "'C:/Users/cvhLa/Onedrive/Desktop/User input (for direct)/"
                file_path = path_to_file + fileName_direc
                robot_root = "'root@"
                robot_ip = robot_ip["OT2L"]
                robot_rest = ":/var/lib/jupyter/notebooks/UserInputs'"
                path_robot = robot_root+robot_ip+robot_rest
                OT2_key = "C:/Users/cvhLa/ot2_ssh_key_OT2L "
                scp = "scp -i "
                
                #scp -i C:/Users/cvhLa/ot2_ssh_key_OT2L 'C:/Users/cvhLa/OneDrive/Desktop/Direct Protocols/README.jpg' root@169.254.212.60:/var/lib/jupyter/notebooks
                Full_command = scp + OT2_key + file_path + path_robot
                completed = subprocess.run(["powershell", "-Command", Full_command], capture_output=True)
                print(completed)
            except: #when it fails you get a popup saying there might not be connection
                sg.Popup("No connection to the robot (is it all just a simulation?)\n"
                         "Or the file was not send")
                 
        elif(values[4] == True):
            #when value 4 is true then the OT2R is selected and the script tries to send the csv to the jupyter
            try:
                popup_connecting()
                fileName_direc = file_name_meta + '.csv'+ '\'' + " "
                path_to_file = "'C:/Users/cvhLa/Onedrive/Desktop/User input (for direct)/"
                file_path = path_to_file + fileName_direc
                robot_root = "'root@"
                robot_ip = robot_ip["OT2R"]
                robot_rest = ":/var/lib/jupyter/notebooks/UserInputs'"
                path_robot = robot_root+robot_ip+robot_rest
                OT2_key_right = "C:/Users/cvhLa/ot2_ssh_key_OT2R "
                scp = "scp -i "
                
                #scp -i C:/Users/cvhLa/ot2_ssh_key_OT2L 'C:/Users/cvhLa/OneDrive/Desktop/Direct Protocols/README.jpg' root@169.254.212.60:/var/lib/jupyter/notebooks
                Full_command = scp + OT2_key_right + file_path + path_robot
                completed = subprocess.run(["powershell", "-Command", Full_command], capture_output=True)
                print(completed)
            except:#when it fails you get a popup saying there might not be connection NOTE: It might not give a vailure because it promps powershell correctly 
                sg.Popup("No connection to the robot (is it all just a simulation?)\n"
                         "Or the file was not send")
        else:
            sg.Popup("Check one of the options", keep_on_top = True)
    
    #events of the webdriver side    
    elif(event == "Save User Inputs"):
        try: 
            if(values['Browse'] == ""):
                sg.Popup("you have not filled in the platemap")
            else:
                #gives all the values its own variable
                filepath = values['Browse']
                pmid_plate = values[0]
                Firstlast = values[1].split(" ")
                Firstname = Firstlast[0]
                Lastname = Firstlast[1]
                Experiment_name = values[2]
                Experiment_num = values[3]
                fullpath = os.path.abspath(filepath)
                
                #set the options for new location for downloaded Robot commands
                options = Options()
                options.set_preference("browser.download.folderList", 2)
                options.set_preference("browser.download.manager.showWhenStarting", False)
                print(simulation)
                if (simulation == "1"):
                    options.set_preference("browser.download.dir", r"C:\Users\jornb\Documents\GitHub\ot2new\Execution code for OT2\Incubator\OT2DirectprotocolCustomizer\Webdriver\Firefox download test")
                    service = Service(executable_path='C://Users//jornb//Documents//GitHub//ot2new//Execution code for OT2//Incubator//OT2DirectprotocolCustomizer//Webdriver//Firefox webdriver//geckodriver')
                else:
                    options.set_preference("browser.download.dir", r"C:\Users\cvhLa\Onedrive\Desktop\User input (for direct)")
                    service = Service(executable_path='C://Users//cvhLa//OneDrive//Desktop//DO NOT TOUCH THIS FOLDER (webdriver)//geckodriver')
                options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/x-gzip")
                
                
                
                if(values[6] == True and values[9] == False and values[8] == False):
                    sg.Popup("Please make sure you select if you want to have the robot fill the wells for you")
                elif(values[6] == False and values[7] == False and values[4] == False and values[5] == False):
                    sg.Popup("You seem to have not selected the method")            
                else:
                    sg.Popup("Make sure your platemap is correct")
                    window["Send to Server"].update(disabled=False)
        except:
            sg.Popup ("Some expected fields were not filled in or incorrectly")
        
        
    elif(event == "Send to Server"):
        #service path is for the gecko executable (needs changed if used on the real pc)
        if(values[4] == True):
            driver = webdriver.Firefox(service = service, options = options)
            driver.get("https://vanhasseltlab.lacdr.leidenuniv.nl/ot2/CQ_Plate/")
            assert "CQ Plate.title"
            filesending = Filesending(fullpath, pmid_plate, Firstname, Lastname, Experiment_name, Experiment_num, simulation)
        
        elif(values[5] == True):
            driver = webdriver.Firefox(service = service, options = options)
            driver.get("https://vanhasseltlab.lacdr.leidenuniv.nl/ot2/MVPlate/")
            assert "Multiplate MIC - OT2 Commander.title"
            filesending = Filesending(fullpath, pmid_plate, Firstname, Lastname, Experiment_name, Experiment_num, simulation)
            
        elif(values[6] == True):
            driver = webdriver.Firefox(service = service, options = options)
            driver.get("https://vanhasseltlab.lacdr.leidenuniv.nl/ot2/Plate384/")
            assert "MIC - 384 Well Plate.title"
            fillingrobot = values[8]
            notfillingrobot = values[9]
            filesending = Filesending384(fullpath, fillingrobot, notfillingrobot, pmid_plate, Firstname, Lastname, Experiment_name, Experiment_num, simulation)
        
        elif(values[7]== True):
            driver = webdriver.Firefox(service = service)
            driver.get("https://vanhasseltlab.lacdr.leidenuniv.nl/ot2/M9MixR/")
            assert "M9 MixR.title"
            filesending = Filesending(fullpath, pmid_plate, Firstname, Lastname, Experiment_name, Experiment_num, simulation)
            
        else:
            sg.Popup('Please select the method you want to use (the app is going to crash now)')
            window.close()
        
window.close()  


