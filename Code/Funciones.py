from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from datetime import datetime
import pandas as pd
import json
import os
import re

def GoToURL(driver,IP,JobName,FromDate,ToDate):
	driver.get(f"{IP}?jobname={JobName}&txtFromDate={FromDate}&txtFromTime=00:00&txtToDate={ToDate}&txtToTime=23:59&nodeid=&foldername=&aplicacion=")
	try:
		WebDriverWait(driver, 20).until(expected_conditions.presence_of_element_located((By.ID, "imprimir")))
	except:
		print("La pagina se demoro mucho en responder")
		driver.close()
	return

def InventarioJobs(Tablas):
	TableroIngestas = r'./Code/TableroIngestas/02. Tablero Seguimiento de Ingestas.xlsx'
	Ingestas_df = pd.read_excel(TableroIngestas, sheet_name='Concentradora Estatus',header = 1, dtype = 'object')[["#Folio","ID Tabla","SDATOOL-Nombre Proyecto","Nombre de la Tabla Master"]]
	Ingestas_df=Ingestas_df[Ingestas_df["SDATOOL-Nombre Proyecto"]=="32335-CDD Based Reporting"]
	col=["Tabla","JOB_NAME","JSONNAME","Tipo_JOB","Frecuencia_Ejecucion","Folio","IdTabla"]
	Lista_df =pd.DataFrame(columns=col)

	for Tabla in Tablas:
		UUAA=Tabla[2:6]
		Objeto=Tabla[7:].replace("_","")
		Folio="[Folio]"
		IdTabla="[IdTabla]"

		if UUAA[0] == 'p': Ingesta = 'Local'
		else: Ingesta = 'Global'
		Folio_df =  Ingestas_df[Ingestas_df["Nombre de la Tabla Master"]==f"{Tabla}"]["#Folio"]
		IdTabla_df = Ingestas_df[Ingestas_df["Nombre de la Tabla Master"]==f"{Tabla}"]["ID Tabla"]
		if not Folio_df.empty:
			Folio=Folio_df.to_string(index=False).replace("\n","_").replace(" ","")
		
		if not IdTabla_df.empty:
			IdTabla=IdTabla_df.to_string(index=False).replace("\n","_").replace(" ","")

		Lista_Temp = pd.DataFrame(BuscarJob(col,Ingesta,Tabla,UUAA,Objeto,Folio,IdTabla),columns=col)
		Lista_df = pd.concat([Lista_df,Lista_Temp], ignore_index=True)
	return Lista_df

def ListarXML(Ingesta,UUAA):
	contenido = []
	if os.path.exists(f'./Code/XML/{Ingesta}/{UUAA}'):
		contenido = os.listdir(f'./Code/XML/{Ingesta}/{UUAA}')
	return contenido

def BuscarJob(col,Ingesta,Tabla,UUAA,Objeto,Folio,IdTabla):
	Lista = []
	ListXML = ListarXML(Ingesta,UUAA)
	for XML in ListXML:
		doc = etree.parse(f'./Code/XML/{Ingesta}/{UUAA}/{XML}')
		DEFTABLE=doc.getroot()[0]
		ListJobName=[]
		JobList=[]
		for Job in DEFTABLE.iterchildren("JOB"):
			DESCRIPTION=dict(Job.items())["DESCRIPTION"]
			JOB_NAME = dict(Job.items())["JOBNAME"]
			JSONNAME = ""
			TipoJOb = ""
			if "CMDLINE" in Job.keys():
				CMDLINE = dict(Job.items())["CMDLINE"]
				ListParam = re.findall(r"%%\w+",CMDLINE)
				for Row in Job.iterchildren():
					RowDict = dict(Row.items())
					if Row.tag not in ["VARIABLE","INCOND"]:
						continue
					if Row.tag == 'VARIABLE' and RowDict["NAME"] in ListParam:
						CMDLINE=CMDLINE.replace(RowDict["NAME"],RowDict["VALUE"])
					if re.search(f'{Objeto}|{Tabla}',CMDLINE+DESCRIPTION):
						#try
						if re.search(r"(?<=-jn\s).\S+|(?<=--transferId\s).\S+",CMDLINE):JSONNAME=re.findall(r"(?<=-jn\s).\S+|(?<=--transferId\s).\S+",CMDLINE)
					if Row.tag =="INCOND":
						listIncond=RowDict["NAME"].split('-TO-')
						if listIncond[0] in ListJobName and listIncond[1] not in ListJobName:
							JobList.append(listIncond[1])

				if re.search(f'{Objeto}|{Tabla}',CMDLINE+DESCRIPTION) or JOB_NAME in JobList:

					if re.search(r"(?<=.pro\s).\S+(?=\s'_id)",CMDLINE):
						JSONNAME=re.findall(r"(?<=.pro\s).\S+(?=\s'_id)",CMDLINE)[0]
						TipoJOb = "FILE WATCHER"

					if re.search(r"(?<=--transferId\s).\S+",CMDLINE):
						JSONNAME=re.findall(r"(?<=--transferId\s).\S+",CMDLINE)[0]
						TipoJOb = "TRANSFERENCIA"

					if re.search(r"(?<=-jn\s).\S+",CMDLINE):
						JSONNAME=re.findall(r"(?<=-jn\s).\S+",CMDLINE)[0]
						if re.search(r"-pe-krb-inr-",CMDLINE):
							TipoJOb = "INGESTA RAW"
						elif re.search(r"-pe-krb-inm-",CMDLINE):
							TipoJOb = "INGESTA MASTER"
						elif re.search(r"-pe-krb-out-",CMDLINE):
							TipoJOb = "INGESTA OUTSTAGING"
						elif re.search(r"-pe-spk-qlt-.+s-\S\S",CMDLINE):
							TipoJOb = "HAMMURABI STAGING"
						elif re.search(r"-pe-spk-qlt-.+r-\S\S",CMDLINE):
							TipoJOb = "HAMMURABI RAW"
						elif re.search(r"-pe-spk-qlt-.+m-\S\S",CMDLINE):
							TipoJOb = "HAMMURABI MASTER"
						elif re.search(r"-pe-dfs-ren-",CMDLINE):
							TipoJOb = "MOVE (HDFS)"
						elif re.search(r"-pe-dfs-rmv-",CMDLINE):
							TipoJOb = "BORRADO"
					ListJobName.append(JOB_NAME)
					FrecEjec = "DAILY" if JOB_NAME[-4] =='0' else "MONTHLY"
					Lista.append([Tabla,JOB_NAME,JSONNAME,TipoJOb,FrecEjec,Folio,IdTabla])
					######BUSQUEDA ANTERIOR
					#if len(ListJobName) == 1:
					#	Buscar = False
					#	for Job2 in DEFTABLE.iterchildren("JOB",reversed=True):
					#		if Buscar:
					#			###
					#			###
					#		if Job == Job2:
					#			Buscar = True
	return Lista

def PrintJob(driver,JobName,FromDate,ToDate,Imprimir):
	Observaciones = ""
	OK = ""
	NOTOK = ""
	OK_List = []
	NOTOK_List = []
	n_rows = 0

	SelectResul = driver.find_element(By.XPATH,'//*[@id="destino"]/div')
	if SelectResul.get_attribute('class') == 'isa_info':
		Observaciones = "No hay registros"
	else:
		n_rows =len(driver.find_elements(By.XPATH,'//*[@id="tblEjec"]/tbody/tr'))
		for row in range(1,n_rows+1):
			ODATE = driver.find_element(By.XPATH,f'//*[@id="tblEjec"]/tbody/tr[{row}]/td[8]').text
			STATUS = driver.find_element(By.XPATH,f'//*[@id="tblEjec"]/tbody/tr[{row}]/td[13]/a').text
			if STATUS == "OK":
				OK_List.append(ODATE)
			else:
				NOTOK_List.append(ODATE)
		OK = "{:.1f}% ({})".format((len(OK_List)/n_rows)*100,len(OK_List))
		NOTOK = "{:.1f}% ({})".format((len(NOTOK_List)/n_rows)*100,len(NOTOK_List))
		Dif = set(NOTOK_List).difference(set(OK_List))
		if len(Dif) == 0:
			Observaciones = "Sin Observaciones"
		else:
			Observaciones = ', '.join(Dif)
	#\/##\/##\/##\/##\/##\/##\/##\/##\/##
	if Imprimir:
		driver.execute_script('window.print();')
	#/\##/\##/\##/\##/\##/\##/\##/\##/\##

	return [n_rows,OK,NOTOK,Observaciones]

def Print_PDF(driver,download_path,output_path,table_name,file_name):
	path=f'{output_path}/{table_name}'
	os.makedirs(path, exist_ok=True)
	while not os.path.exists(f'{download_path}/Scheduling Batch Data Prod.pdf'):
		pass
	if not os.path.exists(f'{path}/{file_name}.pdf'):
		os.rename(f'{download_path}/Scheduling Batch Data Prod.pdf',f'{path}/{file_name}.pdf')
		while not os.path.exists(f'{path}/{file_name}.pdf'):
			pass
	else:
		i = 1
		while os.path.exists(f'{path}/{file_name}({i}).pdf'):
		  i += 1
		os.rename(f'{download_path}/Scheduling Batch Data Prod.pdf',f'{path}/{file_name}({i}).pdf')
		while not os.path.exists(f'{path}/{file_name}({i}).pdf'):
			pass
	return 

def PrintJobNameDF(DF,CHROMEDRIVER_PATH,download_path,output_path,FromDate,ToDate,IP,Imprimir):
	driver =  DriverInit(CHROMEDRIVER_PATH)
	n_rows_list = []
	OK_list = []
	NOTOK_list = []
	Observaciones_list = []
	table_before=""
	i=1
	for index, row in DF.iterrows():
		table_name=f'{row["Folio"]}-{row["IdTabla"]} - {row["Tabla"]}'
		file_name = row["JOB_NAME"] if row["Tipo_JOB"] =='' else f'{row["JOB_NAME"]} - {row["Tipo_JOB"]}'
		if table_before == table_name:
			i+=1
		else: 
			i=1
		file_name="{:02d}. {}".format(i,file_name)
		GoToURL(driver,IP,row["JOB_NAME"],FromDate[row["Frecuencia_Ejecucion"]],ToDate[row["Frecuencia_Ejecucion"]])
		[n_rows,OK,NOTOK,Observaciones] = PrintJob(driver,row["JOB_NAME"],FromDate[row["Frecuencia_Ejecucion"]],ToDate[row["Frecuencia_Ejecucion"]],Imprimir)
		if Imprimir:
			Print_PDF(driver,download_path,output_path,table_name,file_name)
		n_rows_list.append(n_rows)
		OK_list.append(OK)
		NOTOK_list.append(NOTOK)
		Observaciones_list.append(Observaciones)
		table_before = table_name
	driver.close()
	NDF=DF
	NDF["Ejecuciones"] = n_rows_list
	NDF["OK"] = OK_list
	NDF["NOTOK"] = NOTOK_list
	NDF["Observaciones"] = Observaciones_list
	return NDF

def DriverInit(CHROMEDRIVER_PATH):
	chrome_options = webdriver.ChromeOptions()
	settings = {
	       "recentDestinations": [{
	            "id": "Save as PDF",
	            "origin": "local",
	            "account": "",
	        }],
	        "selectedDestinationId": "Save as PDF",
	        "version": 2
	    }
	prefs = {"printing.print_preview_sticky_settings.appState": json.dumps(settings)}
	chrome_options.add_experimental_option('prefs', prefs)
	chrome_options.add_argument('--kiosk-printing')
	return webdriver.Chrome(chrome_options=chrome_options, executable_path=CHROMEDRIVER_PATH)

def PrintFromExcel(path,download_path,output_path,CHROMEDRIVER_PATH,IP,Imprimir):
	Ingestas_df = pd.read_excel(path, sheet_name='JOBNAME', dtype = 'object')
	Tabla_df = pd.read_excel(path, sheet_name='TABLA', dtype = 'object',usecols="A").dropna()
	Fechas_df = pd.read_excel(path, sheet_name='TABLA', dtype = 'object', index_col = 0, usecols="C:E").dropna()
	table = Tabla_df['TABLA MASTER'].values.tolist()
	FromDate = Fechas_df["FECHA INICIO"].dt.strftime("%Y-%m-%d").to_dict()
	ToDate = Fechas_df["FECHA FIN"].dt.strftime("%Y-%m-%d").to_dict()

	if not Ingestas_df.empty:
		driver =  DriverInit(CHROMEDRIVER_PATH)										#Iniciamos Driver de CHROME
		col = ["Tabla","JOB_NAME","JSONNAME","Tipo_JOB","Frecuencia_Ejecucion","Folio","IdTabla","Ejecuciones","OK","NOTOK","Observaciones"]		
		JOB_list=[]
		table_before=""
		i=1
		for index,data in Ingestas_df.iterrows():
			table_name = f'{data["FOLIO-IDTABLA"]} - {data["TABLA"]}'
			file_name = f'{data["JOBNAME"]} - {data["TIPOJOB"]}'
			Job = data["JOBNAME"]
			DateIn = data["FECHA INICIO"].strftime("%Y-%m-%d")
			DateFin = data["FECHA FIN"].strftime("%Y-%m-%d")
			if table_before == table_name:
				i+=1
			else: 
				i=1
			file_name="{:02d}. {}".format(i,file_name)
			GoToURL(driver,IP,Job,DateIn,DateFin)
			[Ejecuciones,OK,NOTOK,Observaciones] = PrintJob(driver,Job,DateIn,DateFin,Imprimir)
			if Imprimir:
				Print_PDF(driver,download_path,output_path,table_name,file_name)	#Imprimimos JOBNAME desde scheduling
			JOB_list.append([data["TABLA"],Job,data["JSONNAME"],data["TIPOJOB"],data["Frecuencia_Ejecucion"],data["FOLIO-IDTABLA"].split("-")[0].replace(" ",""),data["FOLIO-IDTABLA"].split("-")[1].replace(" ",""),Ejecuciones,OK,NOTOK,Observaciones])
			table_before = table_name
			JOB_df=pd.DataFrame(JOB_list,columns=col)										#Creamos un DataFrame para exportar
			JOB_df.to_excel("./Output/JOB-NAME-LIST.xlsx",sheet_name='JOB-NAME-LIST')		#Agregamos Resultado a la Lista
		driver.close()

	if len(table) != 0:
		Jobs_Table_df = InventarioJobs(table)
		Jobs_Table_df = PrintJobNameDF(Jobs_Table_df,CHROMEDRIVER_PATH,download_path,output_path,FromDate,ToDate,IP,Imprimir)
		Jobs_Table_df.to_excel("./Output/JOB-NAME-TABLE-LIST.xlsx",sheet_name='JOB-NAME-LIST')