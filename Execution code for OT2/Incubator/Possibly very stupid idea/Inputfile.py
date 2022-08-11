import PySimpleGUI as sg
import os

layout = [
    [sg.Text("Please provide information about the OT2 run you want to do")],
    [sg.Text('Name File', size=(15,1)), sg.InputText('Filename')],
    [sg.Text('Experiment Name', size=(15,1)), sg.InputText('Experiment Name')],
    [sg.Text('Your Name', size=(15, 1)), sg.InputText('Yourname')],
    [sg.Text('Date', size=(15, 1)), sg.InputText('yymmdd')],
    [sg.Button("Save")],
    [sg.Button("Close")]
]


window = sg.Window("opentron direct protocol maker", layout)


os.chdir("C://Users//jornb//Documents//GitHub//ot2new//Execution code for OT2//Incubator//Possibly very stupid idea")
lines = []
with open('Directscript.py') as f:
    lines = f.readlines()

while True:
    event, values = window.read()
    
    if event =="Close" or event == sg.WIN_CLOSED:
        break
    if event == 'Save':
        os.chdir("C://Users//jornb//Documents//GitHub//ot2new//Execution code for OT2//Incubator//Possibly very stupid idea//New Direct scripts")
        #print(values)
        Direct_protocol_name= values[3]+values[2]+values[1]
        Truename= (Direct_protocol_name+ '.py')
        try:
            fh = open(Truename, 'r+')
        except FileNotFoundError:
            fh = open(Truename, 'w+')
            
        with open(Truename, 'w+') as file:
                file.write('fileName =' + "\'" + values[0]  + '.csv'+ "\'" "\n")
                file.write('#METADATA----------' "\n" +
                            'metadata = {'+"\n"+"\t"+
                                "\'"+ 'protocolName'"\'"+":"+  "\'" + Direct_protocol_name + "\'" +","+"\n"+"\t"+
                                "\'"+'author'"\'"+":" + "\'" +'Sebastian <sebastian.tandar@gmail.com>' +"\'" +"\'"+ 'Jorn <jornbrink@kpnmail.nl>' + "\'"+"," +"\n"+"\t"+
                                "\'"+'description'"\'"+":" + "\'" +'96 wells plate MIC with p300 possibility'+"\'"+ "\'"+'Usercustomized'+"\'"+","+ "\n"+"\t"+
                                "\'"+'apiLevel'"\'"+":"+"\'" +'2.12'+"\'"+ "\n"+'}\n')
                for asd in lines:
                    file.write(asd)
                
        break
window.close()  


