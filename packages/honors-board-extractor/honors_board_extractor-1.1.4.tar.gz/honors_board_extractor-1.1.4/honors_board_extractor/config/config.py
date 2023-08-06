import pathlib
import os
import shutil
import yarl


class Config:
    """
    This class pulls all of the environment variables, and process them
    into the correct types.

    If the variable is missing from the environment, then it will process
    it to a default value. DB username and password default to None
    unlike other values. The dump dir will default to the current working
    directory.
    """
    def __init__(self, region: str, section: str):
        self.region = region
        self.section = section

        db_ip = os.environ.get(f'{region.upper()}_DB_IP')
        self._db_ip = db_ip if db_ip is not None else '127.0.0.1'

        db_port = os.environ.get(f'{region.upper()}_DB_PORT')
        try:
            self._db_port = int(db_port) if type(db_port) is str else 27017
        except ValueError:
            self._db_port = 27017

        self._db_username = os.environ.get(f'{region.upper()}_DB_USERNAME')
        self._db_password = os.environ.get(f'{region.upper()}_DB_PASSWORD')

        datastore_url = os.environ.get(f'{region.upper()}_DATASTORE_URL')
        self._datastore_url = yarl.URL(datastore_url) \
            if datastore_url is not None \
            else yarl.URL('http://localhost:7030/datastore')

        self._datastore_user = os.environ.get(f'{region.upper()}_DATASTORE_USER')
        self._datastore_password = os.environ.get(f'{region.upper()}_DATASTORE_PASSWORD')

        go_chart_url = os.environ.get(f'{region.upper()}_GO_CHART_URL')
        self._go_chart_url = yarl.URL(go_chart_url) / 'api-v1' / 'multi-honors-chart' / 'png' \
            if go_chart_url is not None \
            else yarl.URL('http://localhost:4000/charts') / 'api-v1' / 'multi-honors-chart' / 'png'

        dump_dir = os.environ.get('DUMP_DIR') if os.environ.get('DUMP_DIR') is not None else './dump'
        self._dir_path = pathlib.Path(dump_dir)

    @property
    def db_ip(self):
        return self._db_ip

    @property
    def db_port(self):
        return self._db_port

    @property
    def db_username(self):
        return self._db_username

    @property
    def db_password(self):
        return self._db_password

    @property
    def datastore_url(self):
        return self._datastore_url

    @property
    def datastore_user(self):
        return self._datastore_user

    @property
    def datastore_password(self):
        return self._datastore_password

    @property
    def go_chart_url(self):
        return self._go_chart_url

    @property
    def dir_path(self):
        return self._dir_path

    def setup_dump_dirs(self):
        self.dir_path.mkdir(exist_ok=True)

        self._dir_path = self.dir_path / f'{self.region}-{self.section}'
        if self.dir_path.exists():
            shutil.rmtree(self.dir_path)

        self.dir_path.mkdir(exist_ok=True)
