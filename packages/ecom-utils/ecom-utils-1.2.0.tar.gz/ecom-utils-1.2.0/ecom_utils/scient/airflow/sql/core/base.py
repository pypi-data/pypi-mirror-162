import datetime as dt
import logging
import os
import pandas as pd

from airflow.models import BaseOperator


def execute_with_conn(conn, query):
	status, message = False, ""
	try:
		cur = conn.cursor()
		cur.execute(query)
		conn.commit()
		status=True
		message="Ok"
	except Exception as e:
		logging.error(f"Error ejecutando consultando: {e}")
		logging.error(f"{query}")
		conn.rollback()
		message=str(e)
	return status, message

class GenerateInsertOperator(BaseOperator):
	template_fields = ["input_file", "output_file"]

	def __init__(self, input_file, output_file, table_name, data_cols, remove_input=True, extras_args=[], sep=",", encoding = "utf-8", *args, **kwargs):
		super(GenerateInsertOperator, self).__init__(*args, **kwargs)

		self.data_cols=data_cols
		self.table_name = table_name
		self.extras_args=extras_args
		self.output_file=output_file
		self.input_file=input_file
		self.remove_input=remove_input
		self.sep= sep
		self.encoding = encoding

	def get_fields(self):
		return tuple(list(self.data_cols.keys()))

	def execute(self, context):
		try:
			df = pd.read_csv(self.input_file, sep=self.sep, encoding=self.encoding, dtype=self.data_cols)
		except pd.errors.EmptyDataError:
			logging.warning("Dataset vacío")
			# Eliminamos archivos
			if self.remove_input:
				os.remove(self.input_file)
			with open(self.output_file, "w") as f:
				f.write("")
			return None


		columns_string = str(list(df.columns))[1:-1].replace("'", "")

		
		query=[]
		for index, row in df.iterrows():
			string="("
			i=0
			for key,d in row.to_dict().items():
				temp_data = d
				if isinstance(d, str) and '\'' in d:
					temp_data=d.replace('\'', '\'\'')

				# 
				if pd.isnull(d) or d in ['NaT', 'None']:
					temp_data = 'null'
			
				if self.data_cols[key] in ["int", "Int64"]:
					string+=f"{temp_data}"
				else:
					string+=f"'{temp_data}'"
				
				if not i == len(row.to_dict().items()) - 1:
					string+=","
				i+=1
			string+=")"

			values_string = f"INSERT INTO {self.table_name} ({columns_string}) VALUES {string} ".replace("'null'", 'NULL')

			for arg_ex in self.extras_args:
				values_string+= arg_ex + ' '

			values_string += ';\n'
			query.append(values_string)
		
		with open(self.output_file, "w") as f:
			f.write("\n".join(query))

		# Eliminamos archivos
		if self.remove_input:
			os.remove(self.input_file)

class PopulateOperator(BaseOperator):
	template_fields = ["query_file", "errors_file"]

	def __init__(self, query_file, conn_id, errors_file=None, remove_input=True, schema=None, data_cols_error=None, *args, **kwargs):
		super(PopulateOperator, self).__init__(*args, **kwargs)
		self.query_file = query_file
		self.conn_id = conn_id

		self.errors_file=errors_file

		self.schema=schema
		self.remove_input=remove_input
		self.data_cols_error = data_cols_error

	def execute(self, context):
		conn=self.get_conn()
		
		with open(self.query_file) as sql:
			errores = []
			#  target error_population_instant error_code error_message
			total_registros = 0 
			insert_ok = 0
			insert_error = 0

			for line in sql:
				clean_query = line.strip()

				if clean_query:
					status, message= execute_with_conn(query=clean_query, conn=conn)# execute_pg(query=clean_query, conn_id=self.POSTGRES_CONN_ID)

					total_registros += 1
					if not status:
						insert_error += 1
						clean_query=clean_query.replace("\'", '+')
						if self.data_cols_error:
							
							error = {
								self.data_cols_error.get('query','query'): clean_query,
								self.data_cols_error.get('error_population_instant','error_population_instant'): dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
								self.data_cols_error.get('error_message','error_message'): message
							}
							
						else:
							
							error = {
								"query": clean_query,
								"error_population_instant": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
								"error_message": message
							}
						
						errores.append(error)
					else:
						insert_ok += 1

	
			logging.info(f'Total de registros {total_registros}, registros insertados con exito {insert_ok}, registros con errores {insert_error}')	

		if self.errors_file and len(errores) > 0:
			df_errores = pd.DataFrame(errores)
			df_errores.to_csv(self.errors_file, index=False)
		
		# Eliminamos archivos
		if self.remove_input:
			os.remove(self.query_file)