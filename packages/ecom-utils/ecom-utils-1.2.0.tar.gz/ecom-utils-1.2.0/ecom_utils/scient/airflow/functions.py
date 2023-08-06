import importlib
import logging
import base64

import pandas as pd
import os

from airflow.hooks.postgres_hook import PostgresHook

from contextlib import contextmanager

# ===========================================
def get_dict_connection(name, settings_modulo):
    x = importlib.import_module(settings_modulo.SETTINGS_MODULE)
    return getattr(x, "DATABASES")[name]

def get_conexion(name, settings_modulo):
    return get_dict_connection(name, settings_modulo)["AIRFLOW_PARAMETERS"]["AIRFLOW_NAME"]

def get_str_conexion_mssql(name, settings_modulo):
	dict_conexion = get_dict_connection(name, settings_modulo)
	driver = dict_conexion["OPTIONS"]["driver"]
	return f'DRIVER={driver};SERVER={dict_conexion["HOST"]};DATABASE={dict_conexion["NAME"]};UID={dict_conexion["USER"]};PWD={dict_conexion["PASSWORD"]}'
# ===========================================

def get_query_from_sql(path_sql):
    f = open(path_sql, "r")
    return f.read().replace('\n', ' ')


@contextmanager
def get_dbconnection(strconn, engine):
    conn = engine.connect(strconn)
    try:
        conn.cursor()
        yield conn
    except Exception as e:
        logging.error(f"{e}")
        return e
    finally:
        conn.commit()
        conn.close()


def to_base_64_logo(path_image):
    with open(path_image, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
        return "data:image/png;base64," + encoded_string.decode('utf-8')

# ================================================================
# Funciones para poblar dimensiones temporales
def _insert_dim_nivel_superior(**context):
	dtypes = context.get("dtypes", None)
	if dtypes is None:
		df = pd.read_csv(context['file_input'])
	else:
		df = pd.read_csv(context['file_input'], dtype=dtypes)
	
	pg_hook = PostgresHook(postgres_conn_id=context["POSTGRES_CONN_ID"])
	conn = pg_hook.get_conn()
	cur = conn.cursor()
	for index, row in df.iterrows():
		mes = row[context['campo_mes']] 
		anio = row[context['campo_anio']] 
		cur.execute(f"select inserta_tiemponivelsuperior('{anio}', '{mes}')")
		conn.commit()

	# Eliminamos Archivo de entrada
	os.remove(context['file_input'])

def _insert_fechas_dim_temporal(**context):
	"""Inserta fechas en tabla
	"""
	
	df = pd.read_csv(context['file_input'])
	pg_hook = PostgresHook(postgres_conn_id=context["POSTGRES_CONN_ID"])
	conn = pg_hook.get_conn()
	cur = conn.cursor()
	for index, row in df.iterrows():
		cur.execute(f"select inserta_tiemponiveldia('{row['fechas']}')")
		conn.commit()

	# Eliminamos Archivo de entrada
	os.remove(context['file_input'])

def _get_fechas_to_create_dim_temporal(**context):

	"""Obtiene las fechas a crear"""

	
	data = pd.read_csv(context['data_input'])
	dim_tiemponiveldia = pd.read_csv(context['dim_tiemponiveldia'])
	fechas = set(data.TabAuxiliarFechaLiq.unique()).difference(set(dim_tiemponiveldia.fecha.unique()))
	fechas_df = pd.DataFrame({'fechas' : list(fechas)})
	fechas_df.to_csv(context['file_output'], index=False)
	
	# Eliminamos Archivos de entrada
	os.remove(context['tabaux'])
	os.remove(context['dim_tiemponiveldia'])

# ================================================================
def _insert_dim_planta(**context):
	dtypes = context.get("dtypes", None)
	if dtypes is None:
		df = pd.read_csv(context['file_input'])
	else:
		df = pd.read_csv(context['file_input'], dtype=dtypes)
	
	# df = df.fillna('None')
	
	pg_hook = PostgresHook(postgres_conn_id=context["POSTGRES_CONN_ID"])
	conn = pg_hook.get_conn()
	cur = conn.cursor()
	
	errors_count = 0
	success_count = 0
	
	for index, row in df.iterrows():
		aptaid=f"{row['ptaid']}::integer"
		asrevid=f"{row['srevid']}::smallint"
		aescid=f"{row['escid']}::smallint"
		acarid=f"{row['carid']}::smallint"
		ajurid=f"{row['jurid']}::smallint"
		aptamarcaba= "true::boolean" if row['ptamarcaba'] == 1 else "false::boolean"
		
		abajfch = "NULL" if row["bajfch"] == "None" else f"'{row['bajfch'].split(' ')[0]}'::timestamp"
		
		amotbajid=f"{row['motbajid']}::smallint"
		
		aptahscat="NULL" if pd.isna(row['ptahscat']) else f"{row['ptahscat']}::integer"
		
		asipnumempl="NULL" if pd.isna(row['sipnumempl']) else f"{row['sipnumempl']}::integer"
		
		aptaultperl=f"{row['ptaultperl']}::integer"
		apptcarid=f"{row['pptcarid']}::integer"
		
		apptafchdesd="NULL" if row["ptafchdesd"] == "None" else f"'{row['ptafchdesd'].split(' ')[0]}'::timestamp"
		apptafchhast="NULL" if row["ptafchhast"] == "None" else f"'{row['ptafchhast'].split(' ')[0]}'::timestamp"

		aptatipo=f"{row['ptatipo']}::smallint"
		
		acant_horas_contrato="NULL" if pd.isna(row['ctocanths']) else f"{row['ctocanths']}::decimal(10,2)"
		
		acuit=f"'{row['cuit']}'::text"

		query = f"select id, message from inserta_dimplanta({aptaid}, {asrevid}, {aescid}, {acarid}, {ajurid}, {aptamarcaba}, {abajfch}, {amotbajid}, {aptahscat}, {asipnumempl}, {aptaultperl}, {apptcarid}, {apptafchdesd}, {apptafchhast}, {aptatipo}, {acant_horas_contrato}, {acuit})" 
		
		
		try:
			cur.execute(query)
			success_count+=1
		except Exception as e:
			errors_count+=1
			logging.error(f"Error ejecutando consulta: {query}")
			logging.error(f"Se ha generado el siguiente mensaje de error: {e}")

		conn.commit()

	logging.info(f"Success query: {success_count}")
	logging.info(f"Errors query: {errors_count}")

	# Eliminamos Archivo de entrada
	os.remove(context['file_input'])

if __name__ == '__main__':
	
	LIQ_CARGO_DATA_COLS = {
		"liqanio": "Int64",
		"liqmes": "Int64",
		"liqtipo": "Int64",
		"liqnro": "Int64", 
		"ptaid": "Int64", 
		"liqrbo": "Int64",
		"liqdiast": "Int64",
		"liqsrip": "Int64", 
		"liqpuroca": "float",
		"liqpurosa": "float",
		"liqajusca": "float",
		"liqajussa": "float",
		"liqasfapur": "float",
		"liqasfaaju": "float",
		"liqdtosley": "float",
		"liqotros": "float",
		"liqliqpuro": "float",
		"liqdedaut": "float",
		"liqapatos": "float",
		"liqapatjub": "float",
		"ptaid": "Int64",
		"perpref": "Int64",
		"perdocid": "Int64",
		"perdigito": "Int64",
		"srevid": "Int64",
		"escid": "Int64",
		"carid": "Int64",
		"jurid": "Int64",
		"ptamarcaba": "Int64",
		"bajfch": "str",
		"motbajid":"Int64",
		"ctocanths":"float",
		"ptahscat":"Int64",
		"sipnumempl":"Int64",
		"ptaultperl":"Int64",
		"pptcarid":"Int64",
		"ptafchdesd":"str",
		"ptafchhast": "str",
		"ptatipo": "Int64",
		"planta_fk": "Int64", 
		"dim_planta_ptaid": "Int64"
	}
	
	context={
		"dtypes":LIQ_CARGO_DATA_COLS,
		"file_input":'/home/lucas/work/projects/airflow/dags/dw_chaco_etl/etl_pon_activos/temp/manual__2022-03-29T20:37:26.997765+00:00_plantaoc_inserts.csv',
		"POSTGRES_CONN_ID":'dw_provincial_local'
	}
	_insert_dim_planta(**context)