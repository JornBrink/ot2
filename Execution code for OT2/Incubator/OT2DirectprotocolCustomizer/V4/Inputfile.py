import PySimpleGUI as sg
import os
import subprocess
import json



#BIG EXPLANATION: Somehow do i have save the input from the main window but the childwindow(network driver) is not yet saved (i have no clue how i did it)
#I have the feeling window.close is the reason but i am not entirely sure

def Mainwindow():
    listofusers = os.listdir('C://Users')
    print(listofusers)
    if ("cvhLa" in listofusers):
            print("nonsimulation mode")
            simulation = "0"
    else:
            simulation = "1"
            print("simulation mode active")
    
    # create the layout with buttons and text
    if (simulation == "1"):
        layout = [
            [sg.Button("Make command list")],
            [sg.Text("Please provide information about the OT2 run you want to do")],
            [sg.Text('Name File (without .csv)', size=(18,1)), sg.InputText('')],                           #values0
            [sg.Text('Experiment Name', size=(18,1)), sg.InputText('')],                                    #values1
            [sg.Text('Your Name', size=(18, 1)), sg.InputText('')],                                         #values2
            [sg.Text('Date (yymmdd)', size=(18, 1)), sg.InputText('')],                                     #values3
            [sg.Text('Which OT2 do you want to use?')],                       
            [sg.Radio('OT2L', "group 1"), sg.Radio('OT2R', "group 1")],                                     #Values4&5
            [sg.Text("What pc is it running on?")],
            [sg.Radio('Jorn', "group 2"), 
             sg.Radio('Sebastian', "group 2"), sg.Radio('OT', "group 2")],                                  #Values[6/7/8]
            [sg.Button("Save"),sg.Button("Send", disabled=True), sg.Button("Close")]
        ]
    else:
        layout = [
            [sg.Text("Please provide information about the OT2 run you want to do")],
            [sg.Text('Name File (without .csv)', size=(18,1)), sg.InputText('')],                           #values0
            [sg.Text('Experiment Name', size=(18,1)), sg.InputText('')],                                    #values1
            [sg.Text('Your Name', size=(18, 1)), sg.InputText('')],                                         #values2
            [sg.Text('Date (yymmdd)', size=(18, 1)), sg.InputText('')],                                     #values3
            [sg.Text('Which OT2 do you want to use?')],                       
            [sg.Radio('OT2L', "group 1"), sg.Radio('OT2R', "group 1")],                                     #Values4&5
            [sg.Text("What pc is it running on?")],
            [sg.Radio('OT', "group 2", default = True)],                                                    #Values[6]
            [sg.Button("Save"),sg.Button("Send", disabled=True), sg.Button("Close")]
            ]
    return sg.Window("Opentron direct protocol maker", layout, finalize = True), simulation

def Webinteraction():
    layout = [
        [sg.Text("lets check if functional")],
        [sg.InputText("")],
        [sg.Button('Saveinput'), sg.Button("Close")]                                                        #This save input isnt yet connected with the other inputs
        ]
    return sg.Window('Webdriver', layout, finalize = True)


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
if ("cvhLa" in listofusers):
    print("nonsimulation mode")
    simulation = "0"
else:
    simulation = "1"
    print("simulation mode active")

#Needs to store the Directscript into memory for later use
os.chdir("C://Users//jornb//Documents//GitHub//ot2new//Execution code for OT2//Incubator//OT2DirectprotocolCustomizer//V3")
lines = []
with open('Directscript.py') as f:
    lines = f.readlines()

#FUNCTIONS----------

def getIPs():
    # load data
    f = open('C://Users//jornb//AppData//Roaming//Opentrons//discovery.json')
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
    
    #Stops everything when user uses the button cancle or closes the window
    if event =="Close" or event == sg.WIN_CLOSED:
        window.close()
        if window == window2:
            window2 == None
        elif window == window1:
            break
        #small little problem --> this will break everything and stop it from reacting but its the best i can do for now
    
    #If user wants to make a commandlist open new window
    if event == 'Make command list':
        window2 = Webinteraction()
    
    
    #If user sets save the file is found and prepared for making the script
    if event == 'Save':
        #put filename = into the script
        os.chdir("C://Users//jornb//Documents//GitHub//ot2new//Execution code for OT2//Incubator//OT2DirectprotocolCustomizer//V4//New Direct scripts")
        print(values)
        if(values[0] == "" or values[1]== "" or values[2]== "" or values[3]== ""):
            sg.Popup("Fill all fields and options", keep_on_top = True)
            break #tempuary measure to break
        else:
            Direct_protocol_name= values[3]+values[2]+values[1]
            Truename= (Direct_protocol_name+ '.py')
            try:
                fh = open(Truename, 'r+')
            except FileNotFoundError:
                fh = open(Truename, 'w+')
                
            #creates the option to create the possiblity for simulations (does not uncomment the simulation underneath the directscript)
            if(values[6] == True and simulation == "1" ):
                active_pc ="Jorn"
            elif(values[7] == True and simulation == "1"):
                active_pc = "Sebastian"
            else:
                active_pc = "OT"
                
            # For the metadata of the script added
            with open(Truename, 'w+') as file:
                    file.write('fileName =' + "\'" + values[0]  + '.csv'+ "\'" "\n" + "\n")
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
                        print ("Simulation mode not available")
                    
           #enables the send button
            window['Send'].update(disabled=False)
        
            # check robot IP
            robot_ip = getIPs()
    
    if event == 'Send':
        #when value 4 is true then the OT2L is selected and the script tries to send the csv to the jupyter
        if(values[4] == True):
            try:
                popup_connecting()
                fileName_direc = values[0]  + '.csv'+ '\'' + " "
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
                 
        elif(values[5] == True):
            #when value 4 is true then the OT2R is selected and the script tries to send the csv to the jupyter
            try:
                popup_connecting()
                fileName_direc = values[0]  + '.csv'+ '\'' + " "
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
        
    if event == 'Saveinput':
        window.close()
        print(values)

                
window.close()  


