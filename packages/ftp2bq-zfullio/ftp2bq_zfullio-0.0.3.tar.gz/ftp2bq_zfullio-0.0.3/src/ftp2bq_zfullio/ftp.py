import ftplib


class FTP:

    def __init__(self, host: str, login: str, password: str, port: int = 21):
        self.host = host
        self.port = port
        self.login = login
        self.password = password
        self.connection = None

    def connect(self):
        self.connection = ftplib.FTP()
        self.connection.set_pasv(True)
        self.connection.connect(self.host, self.port, timeout=30)
        self.connection.login(self.login, self.password)

    def ls(self):
        if not self.connection:
            print(f"Нет соединения с {self.host}")
        else:
            return self.connection.nlst()

    def mlsd(self):
        if not self.connection:
            print(f"Нет соединения с {self.host}")
        else:
            return self.connection.mlsd()

    def get(self):
        if not self.connection:
            print(f"Нет соединения с {self.host}")
        else:
            self.connection.retrlines("")

    def download(self, path: str, filename):
        out = path
        if not self.connection:
            print(f"Нет соединения с {self.host}")
        else:
            with open(out, 'wb') as f:
                self.connection.retrbinary(f"RETR {filename}", f.write)
