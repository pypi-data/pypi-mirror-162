import jinja2
import logging
import os
import pandas as pd
import pyodbc

from airflow.models import BaseOperator
from airflow.providers.microsoft.mssql.hooks.mssql import MsSqlHook

from ecom_utils.scient.airflow.functions import get_dbconnection
from ecom_utils.scient.airflow.sql.core.base import GenerateInsertOperator, PopulateOperator

class MSSQLQueryToCSV(BaseOperator):
	template_fields = ["output_file", "render_sql"]

	def __init__(self, query, strconn, output_file, dtypes=None, render_sql=None,*args, **kwargs):
		"""Ejecuta una consulta sobre una base de datos SQL SERVER, devolviendo el resultado en un archivo csv.

		Args:
			query (str): consulta en SQL
			strconn (str): String de Conexion a la BD
			output_file (str): Nombre del arhivo de salida
			dtypes (duct, optional): Tipo de datos de entrada. Defaults to None.
			render_sql (dict, optional): Indica si el archivo SQL necesita ser renderizado con el diccionario que se recibe como parametro. Defaults to None.
		"""
		super(MSSQLQueryToCSV, self).__init__(*args, **kwargs)
		self.query=query
		self.strconn=strconn
		self.output_file=output_file
		self.dtypes=dtypes
		self.render_sql=render_sql

	def execute(self, context):
		if self.render_sql is not None:
			t = jinja2.Template(self.query)
			logging.info("Renderizando consulta...")
			self.query=t.render(self.render_sql)
			
		with get_dbconnection(self.strconn, pyodbc) as conn:
			logging.info(f"Running query: {self.query}")
			
			if self.dtypes is None:
				df = pd.read_sql_query(self.query, conn)
			else:
				df = pd.read_sql_query(self.query, conn, dtype=self.dtypes)

			df.to_csv(self.output_file, index=False)

			logging.info(f"Archivo {self.output_file} creado exitosamente!")

class GenerateInsertMssqlOperator(GenerateInsertOperator):
	pass

# ============================================================


class PopulateMssqlOperator(PopulateOperator):
	def get_conn(self):
		pg_hook = MsSqlHook(mssql_conn_id=self.conn_id, schema=self.schema)
		conn = pg_hook.get_conn()
		return conn