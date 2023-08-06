import numpy as np
from persona_export.configuration.Configuration import Configuration
from .BaseExport import BaseExport
from ..utils.FileOps import FileOps
import os
from pyspark.sql import functions as F


class Connectors(BaseExport):

    def __init__(
            self,
            configuration: Configuration
    ):
        super().__init__(configuration)
        self.configuration = configuration
        self.file_path = f"/local_disk0/data_{self.configuration.get('env')}.h5"
        self.destination = os.path.join(configuration.storage_path, 'hdf/')
        print(f"init of {__name__}")
        
    def join_data_sources(self):
        """
        Join dataframes on FS
        """
        if self.featurestore:
            df = self.load_featurestore().join(self.load_more_data(), on=self.ON_KEY, how='outer')
        else:
            df = self.load_more_data()
        return self.get_sample(df)

    def get_sample(self, df):
        return df.sample(fraction=(1/self.configuration.get('sampling')))

    def define_select(self, definition_persona, definition_base):
        """It select dataframe based on condition in configuration and filter to return column only once"""
        return self.join_data_sources().select(self.get_existing_columns())

    def cast_result_into_float(self):
        not_float_types = ['string', 'int', 'bigint', 'date', 'decimal(38,0)', 'float']
        int_type = ['decimal(38,0)', 'bigint']
        df = self.define_select(None, None)
        for c_name, c_type in df.dtypes:
            if c_type not in not_float_types:
                df = df.withColumn(c_name, F.col(c_name).cast('float'))
            elif c_type in int_type:
                df = df.withColumn(c_name, F.col(c_name).cast('int'))
        return df

    def save_table(self):
        temp_path = f"/dbfs/tmp/data_{self.configuration.get('env')}"
        self.cast_result_into_float().coalesce(1).write.format("parquet").mode("overwrite").save(temp_path)

        # to have nice name in storage for BE 
        FileOps.copy_dbfs(f"{temp_path}/{FileOps.file_list(temp_path)[-1]}",
                          f"{self.destination}/data_{self.configuration.get('env')}.parquet")

        # remove helper parquet after use
        try:
            FileOps.remove_dbfs(temp_path)
        except:
            logging.info('In connector cleanup there is no file to remove or possible to remove.')
