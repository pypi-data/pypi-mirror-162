import os
import typer
from accomate.data.accomate_config import AccomateConfig

from accomate.utils.echo import echo
from accomate.utils.yaml_file import write_yaml_file

database = typer.Typer()

accomate_config: AccomateConfig = AccomateConfig.get_instance()


@database.command()
def config():
    echo("Stating the 🪄️  for database configuration...")
    if not os.path.exists(accomate_config.get_base_db_path()):
        os.mkdir(accomate_config.get_base_db_path())
    base_db_dict = {
        "databases": [
            "mysql",
            "mongo",
            "redis"
        ],
        "clusters": {
            "container": {
                "network": "db-network",
                "type": "mysql",
                "username": "root",
                "password": "weur",
                "port": 3022,
                "volume": ""  # it could be NULL also.
            }
        }
    }
    write_response = write_yaml_file(f'{accomate_config.get_base_db_path()}/config.yaml', base_db_dict)
    if(write_response):
        echo("🙂️ Database configuration is completed")
    else:
        echo("❌️ Failed to configure the database")


def create():
    pass


def connect():
    pass


def remove():
    pass
