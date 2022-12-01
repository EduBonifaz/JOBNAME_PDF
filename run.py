from Code.Funciones import InventarioJobs,PrintFromExcel,Print_PDF,PrintJobNameDF,DriverInit
import pandas as pd
import os
Path =os.getcwd().replace("\\","/")
CHROMEDRIVER_PATH = 	# Colocar Ruta de CHROMEDRIVER
download_path = 		# Colocar Ruta de Descarga del navegador r'C:/Users/user/Downloads'
output_path = f"{Path}/Output/Evidencias"
input_path = r"./Input/INPUT_JOBNAME.xlsx"
IP = "http://172.30.9.229:8080/scheduling/ejecucionesStatus"
Imprimir = True

PrintFromExcel(input_path,download_path,output_path,CHROMEDRIVER_PATH,IP,Imprimir)

print("Finalizo el Programa")#