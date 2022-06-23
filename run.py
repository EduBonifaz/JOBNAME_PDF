from Code.Funciones import InventarioJobs,PrintFromExcel,Print_PDF,PrintJobNameDF,DriverInit
import pandas as pd

download_path = 		# Colocar Ruta de Descarga del navegador r'C:/Users/user/Downloads'
output_path = 			# Colocar Ruta de para almacenar PDF
CHROMEDRIVER_PATH = 	# Colocar Ruta de CHROMEDRIVER
input_path = r"./Input/INPUT_JOBNAME.xlsx"

PrintFromExcel(input_path,CHROMEDRIVER_PATH,download_path,output_path)

#table = [ #Colocar la lista de tablas a consultar
#]

#FromDate = {	"DAILY" : "01-04-2022",			#Editar Rango de fechas para la consulta
#			"MONTHLY" : "01-02-2022"}

#ToDate = {	"DAILY" : "30-04-2022",
#			"MONTHLY" : "30-04-2022"}

#Busca los Jobs en los XML y crea un DataFrame
#Jobs_df = InventarioJobs(table)

#Imprime desde scheduling los Job del DataFrame y añade al DataFrame Estado del JOB
#Jobs_df = PrintJobNameDF(Jobs_df,CHROMEDRIVER_PATH,download_path,output_path,FromDate,ToDate)

#Guarda el DataFrame en Excel
#Jobs_df.to_excel("./Output/JOB-NAME-LIST.xlsx",sheet_name='JOB-NAME-LIST')


#Comando para imprimir una lista de Jobs (ListJob)
#
#ListJob = ['PKCOGCP0004','PKCOGCP0005']										#Lista de Jobs a consultar
#table_name = "Tabla_PKCO"													#Nombre de carpeta a guardar evidencias
#DateIn = "01-04-2022"														#Fecha de Inicio
#DateFin=  "30-04-2022"														#Fecha de Fin
#driver =  DriverInit(CHROMEDRIVER_PATH)										#Iniciamos Driver de CHROME
#driver.get("http://172.30.9.229:8080/scheduling/ejecucionesStatus")					#Abrimos la pagina del scheduling
#col = ["JOBNAME","Ejecuciones","OK","NOTOK","Observaciones"]		
#JOB_list=[]																#Creamos una lista para exportar resultados a excel
#for Job in ListJob:														#Iteramos Lista a consultar
#	file_name=Job															#Opcion para colocar Nombre al PDF exportado (por defecto el nombre del JOBNAME)
#	[Ejecuciones,OK,NOTOK,Observaciones] = Print_PDF(driver,download_path,output_path,table_name,file_name,Job,DateIn,DateFin)	#Imprimimos JOBNAME desde scheduling
#	JOB_list.append([Job,Ejecuciones,OK,NOTOK,Observaciones])						#Agregamos Resultado a la Lista 
#driver.close()															#Cerramos la Pagina 
#
#JOB_df=pd.DataFrame(JOB_list,columns=col)										#Creamos un DataFrame para exportar
#JOB_df.to_excel(f"{output_path}/JOB-NAME-LIST.xlsx",sheet_name='JOB-NAME-LIST')  		#Exportamos a Excel
#

print("Finalizo el Programa")#