import posixpath

from persona_export.configuration import Configuration
from .BaseExport import BaseExport


class DataPlatformExporter(BaseExport):

    def __init__(
            self,
            configuration: Configuration
    ):
        self.data_save_path = configuration.storage_path + 'data_platform/'
        super().__init__(configuration)
        print(f"init of {__name__}")
