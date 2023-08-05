import math

from persona_export.configuration import Configuration
from .BaseExport import BaseExport
from ..utils.FileOps import FileOps


class SalesForceMarketingCloudExporter(BaseExport):
    ONE_GB = (1024 * 1024 * 1024)

    def __init__(
            self,
            configuration: Configuration
    ):
        self.data_save_path = configuration.storage_path + 'Salesforce_MC/'
        super().__init__(configuration)
        print(f"init of {__name__}")

    def save_data(self, df, unix_time, persona):
        name = persona['persona_name']
        persona_id = persona['persona_id']
        csv_location = self.data_location(name, unix_time, persona_id)

        self.add_timestamp(df).coalesce(1).write.option("compression", "gzip")\
            .csv(path=csv_location, mode="append", header="true")

        if FileOps.size(csv_location) / self.ONE_GB > 1.5:
            no_repartition = math.ceil(FileOps.size(csv_location) / self.ONE_GB > 1.5)

            df = self.spark.read.csv(csv_location)
            df.repartition(no_repartition).write.option("compression", "gzip")\
                .csv(path=csv_location, mode="overwrite", header="true")
