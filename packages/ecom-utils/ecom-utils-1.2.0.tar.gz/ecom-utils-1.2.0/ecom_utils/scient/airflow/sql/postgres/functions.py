from airflow.utils.task_group import TaskGroup

from ecom_utils.scient.airflow.sql.postgres.operators import PopulatePostgresOperator, GenerateInsertPostgresOperator

def postgres_populate(group_id, insert_task_id, insert_input_file, insert_input_output_file, insert_table_name, insert_data_cols, populate_task_id, populate_conn_id, encoding = "utf-8", sep=",", remove_input=True, populate_errors_file=None, insert_extras_args=[]):
	with TaskGroup(group_id, tooltip=f"Tasks for {group_id}") as xxx:
		task_1 = GenerateInsertPostgresOperator(
			task_id=insert_task_id,
			input_file=insert_input_file,
			output_file=insert_input_output_file, 
			table_name=insert_table_name, 
			data_cols=insert_data_cols,
			extras_args=insert_extras_args,
			remove_input=remove_input,
			sep=sep, 
			encoding=encoding
		)
		task_2 = PopulatePostgresOperator(
			task_id=populate_task_id,
			POSTGRES_CONN_ID=populate_conn_id,
			query_file=insert_input_output_file,
			errors_file=populate_errors_file,
			remove_input=remove_input
		)

		task_1 >> task_2
	return xxx