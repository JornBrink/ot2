#imports
import FreeSimpleGUI as sg
import os
import shutil
import subprocess
import json
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from pathlib import Path
from urllib.request import urlopen


# old script:
def Filesending(fullpath, pmid_plate, Firstname, Lastname, Experiment_name, Experiment_num, simulation, path):
    x = 'NA'
    
    #This part searches ID of the HTML and adds the variables to it
    driver.find_element(By.ID, "file").send_keys(fullpath)
    driver.find_element(By.ID, "pmid").send_keys(pmid_plate)
    driver.find_element(By.ID, "f_name").send_keys(Firstname)
    driver.find_element(By.ID, "l_name").send_keys(Lastname)
    driver.find_element(By.ID, "exp_name").send_keys(Experiment_name)
    driver.find_element(By.ID, "exp_num").send_keys(Experiment_num)
    
    #Sleep timers to not try to click the download button before server is ready
    time.sleep(3)
    driver.find_element(By.ID, "do").click()
    time.sleep(3)
    textFromDiv = driver.find_element(By.XPATH, "//div[@class='shiny-text-output shiny-bound-output']").text
    file_name = "CommandList_" + textFromDiv + ".csv"
    
    if(simulation== "1"):
        path_to_cmd = path + "//Webdriver//Firefox download test" + '//' + file_name
    else:
        path_to_cmd = path + "//Desktop//User input (for direct)" + '//' + file_name
    
    checkfilepresent=os.path.isfile(path_to_cmd)
    
    #This is a recommendation --> it checks if the file already is present, with the input from a few variables before.
    if(checkfilepresent == True):
        #If the filename already exists this might lead to problems with the further processing of the file. Also forces people to think about their names (when using the app)
        sg.Popup("The file name is already taken please change this", keep_on_top=True)
        driver.close()
    
    else:
        #if not it will download the files
        driver.find_element(By.ID, "d_OT2").click()
        time.sleep(3)
        driver.find_element(By.ID, "guide").click()
        
        #checks another time if the command file exists.
        time.sleep(3)
        checkdownload = os.path.isfile(path_to_cmd)
        oldpath = path.replace('//OneDrive', '')
        oldpath = oldpath + "//Downloads//" + file_name
        if (checkdownload == False):
            os.replace(oldpath, path_to_cmd)
        
        RSP = "Robothandler_" + textFromDiv + ".xlsx"
        
        if(simulation == "1"):
            path_to_RSP = "C://Users//jornb//Documents//GitHub//ot2new//Execution code for OT2//Incubator//OT2DirectprotocolCustomizer//Webdriver//Firefox download test" + '//' + RSP
        else:
            path_to_RSP = path + "//User input (for direct)//" + RSP
        
        checkdownloadrsp = os.path.isfile(path_to_RSP)
        
        if(checkdownload == False):
            driver.find_element(By.ID, "d_OT2").click()
            if(simulation == "1"):
                new_pathRSP = "C://Users//jornb//Downloads//" + RSP
            else:
                new_pathRSP = path + "//Downloads//" + RSP

        elif(checkdownloadrsp == False):
            driver.find_element(By.ID, "guide").click()
            if(simulation == "1"):
                new_pathRSP = "C://Users//jornb//Downloads//" + RSP
            else:
                new_pathRSP = path + "//Downloads//" + RSP
        
        else:
            if(simulation == "1"):
                new_pathRSP = "C://Users//jornb//Downloads//" + RSP
            else:
                new_pathRSP = path + "//Downloads//" + RSP
        
        try:
            os.replace(path_to_RSP, new_pathRSP)
        except:
            pass
        
        sg.Popup("Files should be downloaded(click OK when ready to close browser and continue)", keep_on_top = True)
        
        x = "CommandList_" + textFromDiv
        driver.close()
        #X is the command list so it appears in the Main window
    return x

#completely the same as the previous file sending with only minor changes
def Filesending384(fullpath, fillingrobot, notfillingrobot, pmid_plate, Firstname, Lastname, Experiment_name, Experiment_num, simulation, path):
    x = 'NA'
    fileinput = driver.find_element(By.ID, "file").send_keys(fullpath)
    if (fillingrobot == True):
        driver.find_element(By.ID, "fillOuter").click()
    else:
        print("no outerwell will be filled by OT") 
    
    driver.find_element(By.ID, "file").send_keys(fullpath)
    driver.find_element(By.ID, "pmid").send_keys(pmid_plate)
    driver.find_element(By.ID, "f_name").send_keys(Firstname)
    driver.find_element(By.ID, "l_name").send_keys(Lastname)
    driver.find_element(By.ID, "exp_name").send_keys(Experiment_name)
    driver.find_element(By.ID, "exp_num").send_keys(Experiment_num)
    
    #these sleeptimers are so it doesnt just try to download or click something while this is not possible or might give some problems
    time.sleep(2)
    driver.find_element(By.ID, "do").click()
    time.sleep(3)
    textFromDiv = driver.find_element(By.XPATH, "//div[@class='shiny-text-output shiny-bound-output']").text
    file_name = "CommandList_" + textFromDiv + ".csv"
    
    if(simulation == "1"):
        path_to_cmd = "C://Users//jornb//Documents//GitHub//ot2new//Execution code for OT2//Incubator//OT2DirectprotocolCustomizer//Webdriver//Firefox download test" + '//' + file_name
    else:
        path_to_cmd = path + "//Desktop//User input (for direct)//" + file_name
    
    checkfilepresent=os.path.isfile(path_to_cmd)
    
    #This is a recommendation --> it checks if the file already is present, with the input from a few variables before.
    if(checkfilepresent == True):
        #If the filename already exists this might lead to problems with the further processing of the file. Also forces people to think about their names (when using the app)
        sg.Popup("The file name is already taken please change this", keep_on_top=True)
        driver.close()
    
    else:
        #if not it will download the files
        driver.find_element(By.ID, "d_OT2").click()
        time.sleep(3)
        driver.find_element(By.ID, "guide").click()
        #checks another time if the command file exists.
        time.sleep(3)
        checkdownload = os.path.isfile(path_to_cmd)
        oldpath = path.replace('//OneDrive', '')
        oldpath = oldpath + "//Downloads" + '//' + file_name
        if (checkdownload == False):
            os.replace(oldpath, path_to_cmd)
        RSP = "Robothandler_" + textFromDiv + ".xlsx"
        
        if(simulation == "1"):
            path_to_RSP = "C://Users//jornb//Documents//GitHub//ot2new//Execution code for OT2//Incubator//OT2DirectprotocolCustomizer//Webdriver//Firefox download test" + '//' + RSP
        else:
            path_to_RSP = path + "//Desktop//User input (for direct)" + '//' + RSP
        checkdownloadrsp = os.path.isfile(path_to_RSP)
        
        if(checkdownload == False):
            driver.find_element(By.ID, "d_OT2").click()
        elif(checkdownloadrsp == False):
            driver.find_element(By.ID, "guide").click()
        else:
            if(simulation == "1"):
                new_pathRSP = "C://Users//jornb//Downloads//" + RSP
            else:
                new_pathRSP = path + "//Downloads//" + RSP
            
        try:
            os.replace(path_to_RSP, new_pathRSP)
        except:
            pass
 
        sg.Popup("Files should be downloaded(click OK when ready to close browser and continue)", keep_on_top = True)
        x = "CommandList_" + textFromDiv
        driver.close()
    return x


options.set_preference("browser.download.dir", r"C:\Users\jornb\Documents\GitHub\ot2new\Execution code for OT2\Incubator\OT2DirectprotocolCustomizer\Webdriver\Firefox download test")
service = Service(executable_path= path + '//Webdriver//Firefox webdriver//geckodriver.exe')

    if(event == "Send to Server"):
        #Start webdriver with the executable_paths. If the computer changes then you need to change this in the service section and the options values
        if(values['Checker'] == True):
            driver = webdriver.Firefox(service = service, options = options)
            driver.get("https://ot2.lacdr.leidenuniv.nl/ot2/CQ_Plate/")
            assert "CQ Plate.title"
            x = Filesending(fullpath, pmid_plate, Firstname, Lastname, Experiment_name, Experiment_num, simulation, path)
        
        elif(values['MVP'] == True):
            driver = webdriver.Firefox(service = service, options = options)
            driver.get("https://ot2.lacdr.leidenuniv.nl/ot2/MVPlate/")
            assert "Multiplate MIC - OT2 Commander.title"
            x = Filesending(fullpath, pmid_plate, Firstname, Lastname, Experiment_name, Experiment_num, simulation, path)
            
        elif(values['384p'] == True):
            driver = webdriver.Firefox(service = service, options = options)
            driver.get("https://ot2.lacdr.leidenuniv.nl/ot2/Plate384/")
            assert "MIC - 384 Well Plate.title"
            fillingrobot = values['Fill']
            notfillingrobot = values['nFill']
            x = Filesending384(fullpath, fillingrobot, notfillingrobot, pmid_plate, Firstname, Lastname, Experiment_name, Experiment_num, simulation, path)
        
        elif(values['M9MixR']== True):
            driver = webdriver.Firefox(service = service, options = options)
            driver.get("https://ot2.lacdr.leidenuniv.nl/ot2/M9MixR/")
            assert "M9 MixR.title"
            x = Filesending(fullpath, pmid_plate, Firstname, Lastname, Experiment_name, Experiment_num, simulation, path)
        
        elif(values['Sp']== True):
            driver = webdriver.Firefox(service = service, options = options)
            driver.get("https://ot2.lacdr.leidenuniv.nl/ot2/SingleplateMIC/")
            assert "Singleplate MIC - OT2 Commander.title"
            x = Filesending(fullpath, pmid_plate, Firstname, Lastname, Experiment_name, Experiment_num, simulation, path)  
        
        elif(values['48w'] == True):
            driver = webdriver.Firefox(service = service, options = options)
            driver.get("https://ot2.lacdr.leidenuniv.nl/ot2/Plate48/")
            assert "48 Well Plate.title"
            fillingrobot = values['Fill']
            notfillingrobot = values['nFill']
            x = Filesending384(fullpath, fillingrobot, notfillingrobot, pmid_plate, Firstname, Lastname, Experiment_name, Experiment_num, simulation, path)    
        
        else:
            sg.Popup('Please select the method you want to use (the app is going to crash now)')
            window.close()