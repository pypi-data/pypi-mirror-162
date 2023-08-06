
import os
from pathlib import Path

from persona_export.configuration.Configuration import Configuration
from persona_export.services.ServiceProvider import ServiceProvider


def router(destination_type: str, configuration: Configuration):
    """
    Take destinations list and sort it into classes
    :param:
    :return:
    """

    # should throw and exception if destination is not located
    # or load dummyExport
    service = ServiceProvider.get(destination_type)
    return service(configuration)


def run(configuration_path, storage_path=None):
    config = Configuration.from_path(configuration_path, storage_path)
    service = router(config.get('destination_type'), config)
    service.save_table()


if __name__ == "__main__":
    ROOT_DIR = os.path.dirname(
        os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )
    )  # This is your Project Root

    CONFIG_PATH = os.path.join(ROOT_DIR, "data", "configuration.conf")  # requires `import os`

    run(Path(CONFIG_PATH))
