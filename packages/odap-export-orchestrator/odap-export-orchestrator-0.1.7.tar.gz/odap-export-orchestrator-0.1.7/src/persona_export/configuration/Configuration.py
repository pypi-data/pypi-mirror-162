import logging

from persona_export.utils.FileOps import FileOps


class InvalidConfigurationFileException(Exception):
    """ Throw when configuration file is not in valid format or with missing required fields """


class Configuration:
    """ Hold configuration data """

    REQUIRED_KEYS = ['action', 'destination_type']
    STORAGE_PATH = 'abfss://configtest@adapczpx360lakeg2pg.dfs.core.windows.net/'

    @staticmethod
    def from_path(path: str, storage_path):
        """ Load configuration from source file @path
        :raise FileNotFoundError
        """
        return Configuration(path, storage_path, FileOps.read(path))

    def __init__(self, configuration_path, storage_path, configuration=None):
        """
        Lazy load the configuration file

        :param configuration_path:
        :param configuration:
        """
        self._configuration_path = configuration_path
        self._configuration = configuration
        self._loaded = False
        self._storage_path = storage_path

    @property
    def configuration(self):
        # lazy loading, load when its necessary and try it only once
        not self._loaded and self._load_configuration()
        return self._configuration

    @property
    def storage_path(self):
        if self._storage_path:
            return self._storage_path
        else:
            return self.STORAGE_PATH

    def _load_configuration(self, run_validation=True, force=False):
        """
        Load configuration file. Its possible to force reload config file and turn off validation process by default

        :param run_validation: True by default
        :param force: False by default
        :return:
        :raise InvalidConfigurationFileException when config file is not valid
        """
        if force or not self._configuration:
            self._configuration = FileOps.read(self._configuration_path)

        # run validation
        run_validation and self._is_valid()

        # try loaded only once once
        self._loaded = True

    def _is_valid(self):
        """
        Control if configuration has all necessary parameters and is therefore valid
        :
        :param:
        :return: bool
        :raise InvalidConfigurationFileException when config file is not valid
        """
        if all([key in self._configuration for key in self.REQUIRED_KEYS]):
            return True

        logging.warning("Configuration doesn't have all necessary parameters")
        raise InvalidConfigurationFileException("Missing required field in configuration file")

    def has(self, key: str) -> bool:
        """ Return configuration for obtained key """
        return key in self.configuration

    def get(self, key: str) -> dict:
        """ Return configuration for obtained key """
        return self.configuration.get(key, None)
