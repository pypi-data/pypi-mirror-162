import os, pandas as pd, logging

from airflow.models import BaseOperator

def setup_django_for_airflow(SETTINGS_PATH):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", SETTINGS_PATH)
    
    import django
    django.setup()


class DjangoOperator(BaseOperator):
    def __init__(self, SETTINGS_PATH, *args, **kwargs):
        super(DjangoOperator, self).__init__(*args, **kwargs)
        self.SETTINGS_PATH=SETTINGS_PATH
    
    def pre_execute(self, *args, **kwargs):
        setup_django_for_airflow(self.SETTINGS_PATH)


class LimpiarArhivos(BaseOperator):
    def __init__(self, files, *args, **kwargs):
        super(LimpiarArhivos, self).__init__(*args, **kwargs)
        self.FILES = files

    def execute(self, context):
        for f in self.FILES:
            os.remove(f)


class DfFilterOperator(BaseOperator):
    template_fields = ["input_file", "output_success", "output_unsuccess"]

    def __init__(self, condition, input_file, output_success, output_unsuccess, dtypes, *args, **kwargs):
        """Permite aplicar un conficion de filtro a un dataframe de entrada en formato csv.

        Args:
            condition (str): Condición para filtrar. Sintaxis <column_name> <operator [> < = in]> <comparation> [operator_logic &(and)].
                             Para filtrar por campos nulo/nonulos. Example in condition: column_name.notna()
            input_file (str): Archivo de entrada
            output_success (str): Archivo de salida con los registros que cumplieron la condicion.
            output_unsuccess (str): Archivo de salida con los registros que NO cumplieron la condicion.
            dtypes (dict): Especificacion de tipos de datos de entrada
        """
        super(DfFilterOperator, self).__init__(*args, **kwargs)
        self.condition=condition
        self.input_file=input_file
        self.output_success=output_success
        self.output_unsuccess=output_unsuccess
        self.dtypes=dtypes

    def loggin_count(self, name_df,df):
        logging.info(f"Cantidad de registros en {name_df}: {df.shape[0]}")

    def execute(self, context):
        df=pd.read_csv(self.input_file,dtype=self.dtypes)
        self.loggin_count(self.input_file, df)

        df_filter = df.query(self.condition)
        self.loggin_count(self.output_success, df_filter)

        df_not_filter = pd.concat([df,df_filter]).drop_duplicates(keep=False)
        self.loggin_count(self.output_unsuccess, df_not_filter)

        df_filter.to_csv(self.output_success, index=False)
        df_not_filter.to_csv(self.output_unsuccess, index=False)

        # Eliminamos Archivo de entrada
        os.remove(self.input_file)


class DfTransformOperator(BaseOperator):
    template_fields = ["input_file"]

    def __init__(self, input_file, operations, dtype=None, *args, **kwargs):
        super(DfTransformOperator, self).__init__(*args, **kwargs)
        self.operations=operations
        self.input_file=input_file
        self.dtype=dtype

    def execute(self, context):
        if self.dtype is not None:
            df=pd.read_csv(self.input_file, dtype=self.dtype)
        else:
            df=pd.read_csv(self.input_file)

        renames={}
        for op in self.operations:
            if op["type"] == "add":
                if op["operation"] == "concat":
                    df[op["column_name"]]= df[op["value"]].apply(lambda row: op["separator"].join(row.values.astype(str)), axis=1)
                elif op["operation"] == "fixed":
                    df[op["column_name"]] = op["value"]
            elif op["type"] == "update":
                if op["operation"] == "rename":
                    renames[op["column_name"]]=op["value"]
            elif op["type"] == "remove":
                if op["operation"] == "del":
                    df.drop(op["column_name"], axis=1, inplace=True)
        if renames:
            df.rename(columns=renames, inplace=True)
        df.to_csv(self.input_file, index=False)
        
        
class DfMatchOperator(BaseOperator):
    template_fields = ["input_file_one", "input_file_two", "output_file"]

    def __init__(self, input_file_one, input_file_two, left_on, right_on, output_file, remove_files=True, how="inner", dtypes1=None, dtypes2=None, sep1=",", sep2=",", encoding1=None, encoding2=None,*args, **kwargs):
        super(DfMatchOperator, self).__init__(*args, **kwargs)
        self.input_file_one=input_file_one
        self.input_file_two=input_file_two
        self.how=how
        self.dtypes1=dtypes1
        self.dtypes2=dtypes2
        self.sep1=sep1
        self.sep2=sep2
        self.encoding1=encoding1 
        self.encoding2=encoding2

        self.left_on=left_on
        self.right_on=right_on

        self.output_file=output_file
        self.remove_files=remove_files
    
    def execute(self, context):
        logging.info("Ejecutando DfMatchOperator")
        if self.dtypes1 is not None:
            df1=pd.read_csv(self.input_file_one, dtype=self.dtypes1, sep=self.sep1, encoding=self.encoding1)
        else:
            df1=pd.read_csv(self.input_file_one, sep=self.sep1, encoding=self.encoding1)
        logging.info(f"Lectura exitosa: {self.input_file_one}")

        if self.dtypes2 is not None:
            df2=pd.read_csv(self.input_file_two,dtype=self.dtypes2, sep=self.sep2, encoding=self.encoding2)
        else:
            df2=pd.read_csv(self.input_file_two, sep=self.sep2, encoding=self.encoding2)
        logging.info(f"Lectura exitosa: {self.input_file_two}")

        merge=pd.merge(df1, df2, how=self.how, left_on=self.left_on, right_on=self.right_on)

        merge.to_csv(self.output_file, index=False)

        # Eliminamos Archivo de entrada
        if self.remove_files:
            os.remove(self.input_file_one)
            os.remove(self.input_file_two)

