import PySimpleGUI as sg
import os
import subprocess


layout = [
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

def popup_connecting():
    clicked = sg.PopupOKCancel("This is going to take a bit (might not respond while sending file)\n",
             "Please press OK to continue")
    if (clicked =="OK"):
        return
    else:
        window.close()
    
    return

window = sg.Window("Opentron direct protocol maker", layout)


os.chdir("C://Users//cvhLa//OneDrive//Desktop//Direct Protocols")
lines = []
with open('Directscript.py') as f:
    lines = f.readlines()

while True:
    event, values = window.read()
    
    if event =="Close" or event == sg.WIN_CLOSED:
        break
    if event == 'Save':
        os.chdir("C://Users//cvhLa//OneDrive//Desktop//New Direct scripts")
        print(values)
        Direct_protocol_name= values[3]+values[2]+values[1]
        Truename= (Direct_protocol_name+ '.py')
        try:
            fh = open(Truename, 'r+')
        except FileNotFoundError:
            fh = open(Truename, 'w+')
        
        if(values[6] == True ):
            active_pc ="Jorn"
        elif(values[7] == True):
            active_pc = "Sebastian"
        else:
            active_pc = "OT"
            
        with open(Truename, 'w+') as file:
                file.write('fileName =' + "\'" + values[0]  + '.csv'+ "\'" "\n" + "\n")
                file.write('pc =' + "\'" +active_pc + "\'" + "\n" + "\n")
                file.write('#METADATA----------' "\n" +
                            'metadata = {'+"\n"+"\t"+
                                "\'"+ 'protocolName'"\'"+":"+  "\'" + Direct_protocol_name + "\'" +","+"\n"+"\t"+
                                "\'"+'author'"\'"+":" + "\'" +'Sebastian <sebastian.tandar@gmail.com>' +"\'" +"\'"+ 'Jorn <jornbrink@kpnmail.nl>' + "\'"+"," +"\n"+"\t"+
                                "\'"+'description'"\'"+":" + "\'" +'96 wells plate MIC with p300 possibility'+"\'"+ "\'"+'Usercustomized'+"\'"+","+ "\n"+"\t"+
                                "\'"+'apiLevel'"\'"+":"+"\'" +'2.12'+"\'"+ "\n"+'}\n')
                for asd in lines:
                    file.write(asd)
        print(active_pc)
        window['Send'].update(disabled=False)
    
    if event == 'Send':
        if(values[4] == True):
            try:
                popup_connecting()
                fileName_direc = values[0]  + '.csv'+ '\'' + " "
                path_to_file = "'C:/Users/cvhLa/Onedrive/Desktop/User input (for direct)/"
                file_path = path_to_file + fileName_direc
                path_robot = "'root@169.254.212.60:/var/lib/jupyter/notebooks/UserInputs'"
                OT2_key = "C:/Users/cvhLa/ot2_ssh_key_OT2L "
                scp = "scp -i "
                
                #scp -i C:/Users/cvhLa/ot2_ssh_key_OT2L 'C:/Users/cvhLa/OneDrive/Desktop/Direct Protocols/README.jpg' root@169.254.212.60:/var/lib/jupyter/notebooks
                Full_command = scp + OT2_key + file_path + path_robot
                completed = subprocess.run(["powershell", "-Command", Full_command], capture_output=True)
                print(completed)
            except:
                file_name = values[0]
                home = "C:/Users/jornb/Documents/GitHub/ot2new/Execution code for OT2/Incubator/OT2DirectprotocolCustomizer/V2/New Direct scripts/"
                filepath = home + file_name+".csv"
                sg.Popup("No connection to the robot (is it all just a simulation?)\n"
                         "Or the file was not send")
                 
        elif(values[5] == True):
            try:
                popup_connecting()
                fileName_direc = values[0]  + '.csv'+ '\'' + " "
                path_to_file = "'C:/Users/cvhLa/Onedrive/Desktop/User input (for direct)//"
                file_path = path_to_file + fileName_direc
                path_robot = "'root@169.254.199.130:/var/lib/jupyter/notebooks/UserInputs'"
                OT2_key_right = "C:/Users/cvhLa/ot2_ssh_key_OT2R "
                scp = "scp -i "
                
                #scp -i C:/Users/cvhLa/ot2_ssh_key_OT2L 'C:/Users/cvhLa/OneDrive/Desktop/Direct Protocols/README.jpg' root@169.254.212.60:/var/lib/jupyter/notebooks
                Full_command = scp + OT2_key_right + file_path + path_robot
                completed = subprocess.run(["powershell", "-Command", Full_command], capture_output=True)
                print(completed)
            except:
                file_name = values[0]
                home = "C:/Users/jornb/Documents/GitHub/ot2new/Execution code for OT2/Incubator/OT2DirectprotocolCustomizer/V2/New Direct scripts/"
                filepath = home + file_name+".csv"
                sg.Popup("No connection to the robot (is it all just a simulation?)\n"
                         "Or the file was not send")
        else:
            sg.Popup("Check one of the options", keep_on_top = True)


            
window.close()  


