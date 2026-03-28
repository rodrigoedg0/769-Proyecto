class Usuario:
    def __init__(self, username, password, rol="admin"):
        self.username = username
        self.password = password
        self.rol = rol

    def to_txt(self):
        return f"{self.username},{self.password},{self.rol}\n"