import json
from persona_export.configuration.Configuration import Configuration
from persona_export.sql.BuildCharts import build_charts, Query
from persona_export.sql.QueryBuilder import query_build
from persona_export.utils.FileOps import FileOps
from pyspark.sql import SparkSession


class Insights:

    def __init__(
            self,
            configuration: Configuration
    ):
        self.destination = configuration.storage_path + 'HistorizedInsights/'
        self.spark = SparkSession.builder.getOrCreate()

        self.configuration = configuration
        self.insights = self.configuration.get('params')['insights']

        if self.configuration.get('period_analyse') == 'BEFORE':
            self.analyse = "before_target"
        else:
            self.analyse = 'after_target'

        if 'id_compute' in self.insights:
            self.id_compute = self.insights['id_compute']
        else:
            self.id_compute = 'client_id'

        self.date_from = self.insights['date_from'].replace('-', '')
        self.date_to = self.insights['date_to'].replace('-', '')
        self.period_unit = self.insights['period_unit'].lower()
        self.name = self.configuration.get('name')
        self.tmp_file = f"/dbfs/tmp/{self.name}.json"
        self.file = f"dbfs:/tmp/{self.name}.json"

        self.widgets = {
            "1.get_historized_features": "Yes",
            "2.target_name": f"{self.insights['target']}",
            "3.target_date_from": f"{self.date_from}",
            "4.target_date_to": f"{self.date_to}",
            "5.analyse": f"{self.analyse}",
            "6.number_of_time_units": self.insights['period_time'],
            "7.unit_of_time": f"{self.period_unit}",
            "table_name": f"{self.name}",
            "id_compute": f"{self.id_compute}"
        }

        print(f"init of {__name__}")

    def list_files_name(self):
        return FileOps.file_list("dbfs:/feature_store/")

    def run_dbx_notebook(self):
        """It runs notebook with feature witch we want to compute"""
        if f"{self.name}.delta/" not in self.list_files_name():
            FileOps.run_notebook(self.configuration.get('notebook_path'), 100000, self.widgets)
        return self

    def upload_dataframe_from_featurestore(self):
        self.featurestore = FileOps.read_delta_table(f"dbfs:/feature_store/{self.name}.delta")
        return self

    def turn_dataframe_into_pandas_df(self):
        self.pandas_df = self.featurestore.toPandas()
        return self

    def build_charts(self):
        self.dict_to_save = build_charts(query_string=Query(query=self.get_query()), df_ref=self.pandas_df)
        return self

    def get_query(self):
        """It takes conditions from configuration and change them into string"""
        query = json.dumps(self.configuration.get('params')['conditions'])
        return query_build(json.loads(query))

    def write_tmpfile(self):
        FileOps.write(path=self.tmp_file, data=self.dict_to_save)
        return self

    def copy_to_final_destination(self):
        FileOps.copy_dbfs(path=self.file, destination=f"{self.destination}{self.name}.json")
        return self

    def remove_tmpfile(self):
        FileOps.remove_dbfs(path=self.file)
        return self

    def save_table(self):
        """It save result as json on blob storage"""
        (
            self
                .run_dbx_notebook()
                .upload_dataframe_from_featurestore()
                .turn_dataframe_into_pandas_df()
                .build_charts()
                .write_tmpfile()
                .copy_to_final_destination()
                .remove_tmpfile()
        )
