import json
import logging
import re
import urllib

from pyspark.sql import SparkSession
from pyspark.sql import functions as F

from persona_export.configuration.Configuration import Configuration
from persona_export.sql.QueryBuilder import query_build
from persona_export.utils.FileOps import FileOps


class BaseExport:
    CAST_THRESHOLD = 0.1
    ON_KEY = 'client_id'

    def __init__(self, configuration: Configuration):
        self.configuration = configuration
        self.data_save_path = configuration.storage_path
        self.spark = SparkSession.builder.getOrCreate()
        self.featurestore = self.configuration.get('featurestore') if self.configuration.get('featurestore') else None

    def _is_attributes(self):
        if self.configuration.get('params')['export_columns']:
            return True
        else:
            logging.info("It's persona")

    def download_csv(self, csv_to_read):
        """
        It downloads data from url in data_paths from config
        """
        if 'https' in csv_to_read:
            FileOps.create_folder(f"out/{self.configuration.get('id')}/")
            filename = f"/out/{self.configuration.get('id')}/temporary_1.csv"
            urllib.request.urlretrieve(csv_to_read, "/dbfs" + filename)  # Download files from url
            return self.spark.read.options(header='True', inferschema='True', delimiter=';').csv(filename)
        else:
            return self.spark.read.options(header='True', inferschema='True', delimiter=';').csv(csv_to_read)

    def lowercase_column_names(self, df):
        """It change names of columns into lowercase"""
        return df.toDF(*(c.lower() for c in df.columns))

    def load_data(self, data_path):
        """
        It loads data from csv or delta tables
        """
        if 'csv' in data_path:
            df = self.download_csv(data_path)
            df_recast = self.cast_into_float(self.lowercase_column_names(df))
            return self.cast_client_id_string(df_recast)
        elif re.search(r"^\w+[.]\w+$", data_path):
            df = self.spark.sql(f"""select * from {data_path}""")
            return self.lowercase_column_names(df)
        else:
            try:
                df = FileOps.read_delta_table(data_path)
                return self.lowercase_column_names(df)
            except:
                logging.warning('Not supported format.')

    def cast_into_float(self, df):
        """
        It try to find any columns witch haven't been correctly typed and if they match criteria it cast them into float
        """
        # nacachovat df
        # nebo kolekce do parquetu predtim
        total = df.count()
        ten_percent = total * self.CAST_THRESHOLD
        df2 = df.select(*(F.col(c_name).rlike("^-?[0-9]+[,.]?[0-9]*$")
                        .cast('int').alias(c_name) for c_name, c_type in df.dtypes if c_type == 'string'))
        sums = df2.agg(*[(F.count(df2[c_name]) - F.sum(df2[c_name]))
                       .alias(c_name) for c_name in df2.columns]).collect()[0].asDict()

        for c_name, value in sums.items():
            if value and value < ten_percent:
                df = df.withColumn(c_name, F.col(c_name).cast('float'))

        return df

    def cast_client_id_string(self, df):
        return df.withColumn('client_id', df.client_id.cast('string'))

    def load_featurestore(self):
        """Helper function to read tables into dataframes"""
        if self.featurestore:
            if re.search(r"^\w+[.]\w+$", self.featurestore):
                return self.spark.sql(f"""select * from {self.featurestore}""")
            else:
                return FileOps.read_delta_table(self.featurestore)

    def load_more_data(self):
        """
        If there are more data specified than just joiner or FS, read them as well
        """
        # joiny, nastavit vyssi limit pro broadcast 100MB, jak dlouho muze bezet, default 3 min, popr. zapnout AQE
        table_list = self.configuration.get('data_paths')
        if table_list:
            table = self.load_data(table_list[0])
            if len(table_list) > 1:
                for table_to_join in table_list[1:]:
                    table = table.join(self.load_data(table_to_join), on='client_id', how='outer')
            return table
        else:
            return None

    def join_data_sources(self):
        """
        Join dataframes on FS
        """
        if self.featurestore:
            return self.load_featurestore().join(self.load_more_data(), on=self.ON_KEY, how='outer')
        else:
            return self.load_more_data()

    def get_existing_columns(self):
        """It takes desired columns and compare it with existing columns. Returns only unique existing columns"""
        if isinstance(self.configuration.get('params')['export_columns'], str):
            desired_columns = set(word.lower() for word in (eval(self.configuration.get('params')['export_columns'])) + ['client_id'])
        else:
            desired_columns = set(word.lower() for word in (self.configuration.get('params')['export_columns'] + ['client_id']))
        dataframe_columns = set(word.lower() for word in self.join_data_sources().columns)
        return list(dataframe_columns.intersection(desired_columns))

    def define_select(self, definition_persona, definition_base):
        """It select dataframe based on condition in configuration and filter to return column only once"""
        if definition_base and definition_persona:
            return self.join_data_sources().select(self.get_existing_columns())\
                .filter(f"{definition_persona}" and f"{definition_base}")
        elif definition_base:
            return self.join_data_sources().select(self.get_existing_columns()) \
                .filter(f"{definition_base}")
        elif definition_persona:
            return self.join_data_sources().select(self.get_existing_columns()) \
                .filter(f"{definition_persona}")

    def add_timestamp(self, df):
        df_timestamp = df.withColumn('timestamp', F.current_timestamp())
        return df_timestamp

    def save_table(self):
        unix_time = self.configuration.get('created_at')
        for persona in self.configuration.get('personas'):
            self.save_persona(persona, unix_time)

    def save_persona(self, persona, unix_time):
        persona_query = json.dumps(persona['definition_persona'])
        base_query = json.dumps(persona['definition_base'])

        definition_persona = query_build(json.loads(persona_query))
        definition_base = query_build(json.loads(base_query))

        df = self.define_select(definition_persona, definition_base)
        self.save_data(df, unix_time, persona)

    def data_location(self, name, unix_time, persona_id):
        location = f"{self.data_save_path}/persona/{persona_id}"
        if self._is_attributes():
            location = f"{self.data_save_path}/attributes/{name}_{unix_time}"
        return location

    def delete_temporary_file(self):
        """
        It deletes folder with temporary files
        """
        try:
            FileOps.remove_dbfs(f"dbfs:/out/{self.configuration.get('id')}/")
        except:
            logging.info('Nothing temporary to remove')

    def save_data(self, df, unix_time, persona):
        name = persona['persona_name']
        persona_id = persona['persona_id']
        data_path = self.data_location(name, unix_time, persona_id)

        if self._is_attributes():
            self.add_timestamp(df).write.format("delta").save(data_path)
        else:
            self.add_timestamp(df).write.format("delta").mode("append").save(data_path)
        self.delete_temporary_file()
