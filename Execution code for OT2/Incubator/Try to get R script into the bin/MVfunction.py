#############test filename##########
file_name= "MV_InputTemplate.xlsx"

import csv
import numpy as np
import math as mt
import os
import openpyxl

#########OS (test only)#########

os.chdir('C://Users//jornb//Documents//GitHub//ot2new//Execution code for OT2//Incubator//Try to get R script into the bin//MIC Platemap')
wb = openpyxl.load_workbook(file_name)
sheet = wb.active

cells = sheet['C1','F3']  

for i1,i2 in cells:  

    print("{0:8} {1:8}".format(i1.value,i2.value))  



