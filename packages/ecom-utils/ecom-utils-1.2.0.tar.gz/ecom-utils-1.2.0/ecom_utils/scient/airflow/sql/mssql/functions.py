
from airflow.utils.task_group import TaskGroup

from ecom_utils.scient.airflow.sql.mssql.operators import GenerateInsertMssqlOperator, PopulateMssqlOperator
from ecom_utils.scient.airflow.sql.operators       import DfTransformOperator
from airflow.operators.python import BranchPythonOperator
from airflow.operators.dummy import DummyOperator

def siguiente_tarea(**kwargs):
    import os
    if os.path.exists(kwargs['file_input']):
        task_in_group = kwargs['grupo_id']+'.'+kwargs['task_process_error_id']
        return task_in_group
    else:
        task_in_group = kwargs['grupo_id']+'.'+kwargs['dummy_id']
        return task_in_group

def mssql_populate_errors(group_id, task_id_branch, task_id_dummy,task_id_transform_error,errors_file, col_csv_errores, dag_id, task_id_generate_insert_error,output_file_sql,table_name_error,col_table_error,sep,task_id_populate_tabla_error,conn_id,schema):
    with TaskGroup(group_id, tooltip=f"Tasks for {group_id}") as xxx:

        branch_task = BranchPythonOperator(
            task_id=task_id_branch,
            python_callable=siguiente_tarea,
            op_kwargs={
                "file_input": errors_file,
                "task_process_error_id": task_id_transform_error,
                "dummy_id": task_id_dummy,
                "grupo_id": group_id
            }
        )

        dummy_task = DummyOperator(
            task_id = task_id_dummy
        )

        task_transform_error = DfTransformOperator(
            task_id=task_id_transform_error,
            dtype=col_csv_errores,
            input_file=errors_file,
            operations=[
                {"type": "remove", "column_name": "error_population_instant", "operation": "del"},
                {"type": "add", "column_name": "dag_id", "operation": "fixed", "value":dag_id,"separator":','}
            ]
        )

        task_generate_insert_error=GenerateInsertMssqlOperator(
            task_id=task_id_generate_insert_error,
            input_file=errors_file,
            output_file=output_file_sql,
            table_name=table_name_error, 
            data_cols=col_table_error,
            sep=sep
        )

        task_populate_tabla_error = PopulateMssqlOperator(
            task_id=task_id_populate_tabla_error,
            query_file=output_file_sql,
            conn_id=conn_id, 
            schema=schema,
	    )

        branch_task >> task_transform_error >> task_generate_insert_error >> task_populate_tabla_error
        branch_task >> dummy_task
    return xxx