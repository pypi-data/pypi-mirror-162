import logging
import pandas as pd

from airflow.hooks.postgres_hook import PostgresHook
from airflow.models              import BaseOperator

from ecom_utils.scient.airflow.sql.core.base import GenerateInsertOperator, PopulateOperator

def execute_pg(query, conn_id):
	status, message = False, ""
	try:
		pg_hook = PostgresHook(postgres_conn_id=conn_id)
		conn = pg_hook.get_conn()
		cur = conn.cursor()
		cur.execute(query)
		conn.commit()
		status=True
		message="Ok"
	except Exception as e:
		logging.error(f"Error ejecutando: {query} - {e}")
		message=str(e)
	finally:
		cur.close()
		conn.close()
	return status, message

class PopulatePostgresOperator(PopulateOperator):
	def get_conn(conn_id):
		pg_hook = PostgresHook(postgres_conn_id=conn_id)
		conn = pg_hook.get_conn()
		return conn

class GenerateInsertPostgresOperator(GenerateInsertOperator):
	pass

class PgQueryToCSV(BaseOperator):
	template_fields = ["output_file"]

	def __init__(self, query, postgres_conn_id, output_file, dtypes=None, *args, **kwargs):
		super(PgQueryToCSV, self).__init__(*args, **kwargs)
		self.query=query
		self.postgres_conn_id=postgres_conn_id
		self.output_file=output_file
		self.dtypes=dtypes

	def execute(self, context):
		pg_hook = PostgresHook(postgres_conn_id=self.postgres_conn_id)
		conn = pg_hook.get_conn()

		if self.dtypes is None:
			df = pd.read_sql_query(self.query, conn)
		else:
			df = pd.read_sql_query(self.query, conn, dtype=self.dtypes)


		df.to_csv(self.output_file, index=False)
		logging.info(f"Archivo {self.output_file} creado exitosamente!")