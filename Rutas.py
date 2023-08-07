from pyhocon import ConfigFactory
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
import pandas as pd
import re
import os
import time

CHROMEDRIVER_PATH = r"D:/chromedriver_win32/chromedriver.exe"

options = webdriver.ChromeOptions()
options.add_argument(r'--user-data-dir=C:/Users/user/AppData/Local/Google/Chrome/User Data')
options.add_argument(r'--profile-directory=Profile 1')
driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, options=options)
driver.get('https://www.google.com')

InputXLSX = r'./Output/JOB-NAME.xlsx'
Tablas_df = pd.read_excel(InputXLSX, sheet_name='JOB-NAME-LIST',index_col=0, dtype = 'object')

ResponJob = "Eduardo Bonifaz"
ScrumDesarr = "Skeleton Kappa"
UsuarioResp = ""
CasoUso = "CDD BASED REPORTING"
FechaTraspaso = ""
Pack = ""

Input_bk = ""
Fuente_bk = ""

SizeList = []
URLList = []
UUAAList = []
InputList = []
OutputList = []
OrigenList = []
FuenteList = []
TipoJobList = []
ResponJobList = []
ScrumDesarrList = []
UsuarioRespList = []
CasoUsoList = []
DominioList = []
FechaTraspasoList = []
PackList = []
FaseList = []
DescripcionList = []
VersionSkynetList = []
HistorialList = []

Historial = ""
BusquedaBK = ""
table_before = ""
for item,row in Tablas_df.iterrows():

	URL = "NA"
	Size = "-"
	Input = "-"
	Output = "-"
	Origen = ""
	Fuente = ""
	Dominio = "Engineering"
	Fase = row["Tipo_JOB"]
	Descripcion = ""
	VersionSkynet = "NA"
	Busqueda = ""


	if len(row['JOB_NAME']) == 10:
		UUAA = row['JOB_NAME'][:4]
	elif len(row['JOB_NAME']) == 11:
		UUAA = row['JOB_NAME'][1:5]

	if "HAMMURABI" in row["Tipo_JOB"]:
		[name,num]=row["JSONNAME"].split("-qlt-")[1].split("-")

		JobConf = "/"+row["Tipo_JOB"].split(" ")[1].lower()+"/"+"-".join([name[:-1],num])+".conf"

		driver.get(f'https://globaldevtools.bbva.com/bitbucket/plugins/servlet/search?q=project%3AVBSUU%20"{JobConf}"')
		Busqueda = name[:-1]
		try:
			WebDriverWait(driver, 20).until(expected_conditions.presence_of_element_located((By.XPATH,'//*[@id="codesearch"]/div/div[1]/div/ul')))
			time.sleep(0.2)
			if "" == driver.find_element(By.XPATH,'//*[@id="codesearch"]/div/div[1]/div/ul').text:
				JobConf = "/"+row["Tipo_JOB"].split(" ")[1].lower()+"/"+"-".join([row["Tabla"],num])+".conf"
				driver.get(f'https://globaldevtools.bbva.com/bitbucket/plugins/servlet/search?q=project%3AVBSUU%20"{JobConf}"')
				Busqueda = row["Tabla"]
				WebDriverWait(driver, 20).until(expected_conditions.presence_of_element_located((By.XPATH,'//*[@id="codesearch"]/div/div[1]/div/ul')))
				time.sleep(0.2)
			URL = driver.find_element(By.XPATH,'//*[@id="codesearch"]/div/div[1]/div/ul/li/section/header/a[2]').get_attribute('href')
			driver.get(URL.replace("/browse/","/raw/"))
			try:
				WebDriverWait(driver, 20).until(expected_conditions.presence_of_element_located((By.XPATH,'/html/body/pre')))
				time.sleep(0.2)
				ConfText = driver.find_element(By.XPATH,'/html/body/pre').text
				Variables=re.findall(r"(?<=\$\{)[\?A-Z0-9_]+(?=\})",ConfText)
				Variables = list(set(Variables))
				for data in Variables:
				    if '?' in data:
				        data=data.replace('?','')
				        os.environ[data] = '"${?'+data+'}"'
				    else:
				        os.environ[data] = '"${'+data+'}"'

				Input = "\n".join(ConfigFactory.parse_string(ConfText)["hammurabi.input.paths"])
				Output = "/data/master/dq/haas/t_kqpd_stats"

			except:
				print(row["JSONNAME"],"Fallo2")

			driver.get(URL.replace(".conf",".json").replace("/browse/","/raw/"))
			try:
				WebDriverWait(driver, 20).until(expected_conditions.presence_of_element_located((By.XPATH,'/html/body/pre')))
				time.sleep(0.2)
				JsonText = driver.find_element(By.XPATH,'/html/body/pre').text
				Size = re.findall(r"(?<=\"size\"\s\:\s\")[A-Z]{1,3}(?=\"\,)",JsonText)[0]
				

			except:
				print(row["JSONNAME"],"Fallo1")
		except:
			print(row["JSONNAME"],"Fallo")
		
		if "/in/staging/" in Input:
			Fuente = Input.split("/")[-1]
			Origen = "Staging"
			Fuente_bk = Fuente
			Input_bk = Input
			Descripcion = "Validación de Hammurabi en fase Staging"

		if "/data/raw/" in Input:

			Fuente = re.findall(r"(?<=data/)t_[a-z0-9_]*",Input)[0]
			Origen = "Raw"
			Descripcion = "Validación de Hammurabi en fase Raw"


		if "/data/master/" in Input:
			Fuente = re.findall(r"(?<=data/)t_[a-z0-9_]*",Input)[0]
			Origen = "Master"
			Descripcion = "Validación de Hammurabi en fase Master"

		VersionSkynet = "T-1500.2"


	if "INGESTA" in row["Tipo_JOB"]:
		if row["Tipo_JOB"].split(" ")[1] == "OUTSTAGING":
			Zona = "staging/out"
		else:
			Zona = row["Tipo_JOB"].split(" ")[1].lower()
		[name,num]=row["JSONNAME"].split("-krb-")[1].split("-")[1:]
		JobConf = "/"+UUAA.lower()+"/"+name[:-1]+"/"+Zona+"/"+name[:-1]+".conf"
		driver.get(f'https://globaldevtools.bbva.com/bitbucket/plugins/servlet/search?q=project%3AVBSUU%20"{JobConf}"')
		Busqueda = name[:-1]
		try:
			WebDriverWait(driver, 20).until(expected_conditions.presence_of_element_located((By.XPATH,'//*[@id="codesearch"]/div/div[1]/div/ul')))
			time.sleep(0.2)
			if "" == driver.find_element(By.XPATH,'//*[@id="codesearch"]/div/div[1]/div/ul').text:
				JobConf = "/"+UUAA.lower()+"/"+row["Tabla"]+"/"+Zona+"/"+row["Tabla"]+".conf"
				driver.get(f'https://globaldevtools.bbva.com/bitbucket/plugins/servlet/search?q=project%3AVBSUU%20"{JobConf}"')
				Busqueda = row["Tabla"]
				WebDriverWait(driver, 20).until(expected_conditions.presence_of_element_located((By.XPATH,'//*[@id="codesearch"]/div/div[1]/div/ul')))
				time.sleep(0.2)

			URL = driver.find_element(By.XPATH,'//*[@id="codesearch"]/div/div[1]/div/ul/li/section/header/a[2]').get_attribute('href')

			driver.get(URL.replace("/browse/","/raw/"))
			try:
				WebDriverWait(driver, 20).until(expected_conditions.presence_of_element_located((By.XPATH,'/html/body/pre')))
				time.sleep(0.2)
				ConfText = driver.find_element(By.XPATH,'/html/body/pre').text
				Variables=re.findall(r"(?<=\$\{)[\?A-Z0-9_]+(?=\})",ConfText)
				Variables = list(set(Variables))
				for data in Variables:
				    if '?' in data:
				        data=data.replace('?','')
				        os.environ[data] = '"${?'+data+'}"'
				    else:
				        os.environ[data] = '"${'+data+'}"'

				Input = "\n".join(ConfigFactory.parse_string(ConfText)["kirby.input.paths"])
				Output = ConfigFactory.parse_string(ConfText)["kirby.output.path"]

			except:
				print(row["JSONNAME"],"Fallo2")

			driver.get(URL.replace(".conf",".json").replace("/browse/","/raw/"))
			try:
				WebDriverWait(driver, 20).until(expected_conditions.presence_of_element_located((By.XPATH,'/html/body/pre')))
				time.sleep(0.2)
				JsonText = driver.find_element(By.XPATH,'/html/body/pre').text
				Size = re.findall(r"(?<=\"size\"\s\:\s\")[A-Z]{1,3}(?=\")",JsonText)[0]

			except:
				print(row["JSONNAME"],"Fallo1")
		except:
			print(row["JSONNAME"],"Fallo")

		if "/in/staging/" in Input:
			Origen = "Staging"
		
		if "/data/raw/" in Input:
			Origen = "Raw"

		if "/data/master/" in Input:
			Origen = "Master"

		if "/data/raw/" in Output:
			Fuente = re.findall(r"(?<=data/)t_[a-z0-9_]*",Output)[0]
			Descripcion = "Ingesta de la tabla en fase Raw"

		if "/data/master/" in Output:
			Fuente = re.findall(r"(?<=data/)t_[a-z0-9_]*",Output)[0]
			Descripcion = "Ingesta de la tabla en fase Master"

		if "/out/staging/" in Output:
			Fuente = re.findall(r"(?<=/)t_[a-z0-9_]*",Output)[0]
			Descripcion = "Ingesta de la tabla en fase OutStaging"

		if "/in/staging/" in Input:
			Origen = "Staging"
			if Fuente_bk == "":
				Fuente_bk = Fuente
				Input_bk = Input


		VersionSkynet = "T-1500.2"

	if "BORRADO" in row["Tipo_JOB"]:
		Origen = "Staging"
		if table_before == row["Tabla"]:
			Input = Input_bk
			Fuente = Fuente_bk
			Descripcion = "Job que realiza el borrado del fichero que se encuentra en Staging."
			Dominio = "Client Solution"
			Input_bk = ""
			Fuente_bk = ""

	if BusquedaBK != Busqueda and Busqueda != "" :

		driver.get(URL.split("browse/skynet")[0]+f"pull-requests?state=MERGED&reviewer=&filterText={Busqueda}")
		n_rows =len(driver.find_elements(By.XPATH,r'//*[@id="pull-requests-content"]/div/div[2]/table/tbody/tr'))
		Historial_BK = []
		for n_row in range(1,n_rows+1):
			TipoDev = driver.find_element(By.XPATH,f'//*[@id="pull-requests-content"]/div/div[2]/table/tbody/tr[{n_row}]/td[2]/div[1]/a').text.split(" files for")[0]
			UserDev = driver.find_element(By.XPATH,f'//*[@id="pull-requests-content"]/div/div[2]/table/tbody/tr[{n_row}]/td[2]/div[2]/span').text.split(" - ")[0]
			timeDate = driver.find_element(By.XPATH,f'//*[@id="pull-requests-content"]/div/div[2]/table/tbody/tr[{n_row}]/td[2]/div[2]/time').text
			Historial_BK.append(f"{TipoDev}, {UserDev}, {timeDate}")
		Historial = "\n".join(Historial_BK)
	
	BusquedaBK = Busqueda

	if table_before != row["Tabla"]:
		Historial = ""
		BusquedaBK = ""
	table_before = row["Tabla"]

	URLList.append(URL)
	SizeList.append(Size)
	UUAAList.append(UUAA)
	InputList.append(Input)
	OutputList.append(Output)
	OrigenList.append(Origen)
	FuenteList.append(Fuente)
	TipoJobList.append(row["Tipo_JOB"].split(" ")[0])
	ResponJobList.append(ResponJob)
	ScrumDesarrList.append(ScrumDesarr)
	UsuarioRespList.append(UsuarioResp)
	CasoUsoList.append(CasoUso)
	DominioList.append(Dominio)
	FechaTraspasoList.append(FechaTraspaso)
	PackList.append(Pack)
	FaseList.append(Fase)
	DescripcionList.append(Descripcion)
	VersionSkynetList.append(VersionSkynet)
	HistorialList.append(Historial)

driver.close()

Tablas_df['Folio-Id'] = Tablas_df['Folio'].str.cat(Tablas_df['IdTabla'], sep='-')
Tablas_df = Tablas_df.drop(['Folio', 'IdTabla','Tipo_JOB'], axis=1)
Tablas_df.insert(0, "RUTA_BITBUCKET", URLList)
Tablas_df.insert(0, "Size", SizeList)
Tablas_df.insert(0, "UUAA", UUAAList)
Tablas_df.insert(0, "Input", InputList)
Tablas_df.insert(0, "Output", OutputList)
Tablas_df.insert(0, "Origen", OrigenList)
Tablas_df.insert(0, "Fuente", FuenteList)
Tablas_df.insert(0, "Tipo_JOB", TipoJobList)
Tablas_df.insert(0, "Responsable_Job", ResponJobList)
Tablas_df.insert(0, "Scrum_Desarrollo", ScrumDesarrList)
Tablas_df.insert(0, "USUARIO_RESPONSABLE", UsuarioRespList)
Tablas_df.insert(0, "CASOS_DE_USO", CasoUsoList)
Tablas_df.insert(0, "DOMINIO", DominioList)
Tablas_df.insert(0, "FECHA_TRASPASO", FechaTraspasoList)
Tablas_df.insert(0, "PACK", PackList)
Tablas_df.insert(0, "FASE", FaseList)
Tablas_df.insert(0, "DESCRIPCION", DescripcionList)
Tablas_df.insert(0, "Version_Skynet", VersionSkynetList)
Tablas_df.insert(0, "Historial", HistorialList)
Tablas_df=Tablas_df[['Tabla','JOB_NAME','JSONNAME','Responsable_Job','Scrum_Desarrollo','Frecuencia_Ejecucion','Fuente','Origen','Input','Output','Tipo_JOB','USUARIO_RESPONSABLE','CASOS_DE_USO','DOMINIO','FECHA_TRASPASO','PACK','FASE','DESCRIPCION','Version_Skynet','UUAA','Size','Folio-Id','RUTA_BITBUCKET','Observaciones','Ejecuciones','OK','NOTOK','Historial']]
Tablas_df.to_excel("./Output/JOB-NAME-RUTAS.xlsx",sheet_name='JOB-NAME-LIST')
print("Finalizado")