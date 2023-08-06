from loguru import logger
from paramiko import SSHClient, AutoAddPolicy

from .ftp import FTP


class SFTP(FTP):

    def __init__(self, host: str, login: str, password: str, port: int = 21):
        super().__init__(host, login, password, port)
        self.host = host
        self.port = port
        self.login = login
        self.password = password
        self.client = None

    def connect(self):
        self.client = SSHClient()
        self.client.load_system_host_keys()
        self.client.set_missing_host_key_policy(AutoAddPolicy())
        self.client.connect(self.host, self.port, username=self.login, password=self.password, timeout=4)

    def list(self, path: str):
        with self.client.open_sftp() as sftp:
            try:
                sftp.chdir(path)
                return sftp.listdir_attr()
            except Exception as err:
                logger.warning(f"Ошибка запроса: {err}")

    def get_file(self, path: str, filename: str):
        with self.client.open_sftp() as sftp:
            try:
                sftp.get(f"{path}/{filename}", f"data/{filename}")
            except Exception as err:
                logger.warning(f"Ошибка получения файла: {err}")
