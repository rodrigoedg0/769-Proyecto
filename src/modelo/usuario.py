class Usuario:
    def __init__(self, username, password, rol="operador"):
        self.username = username
        self.password = password
        self.rol = rol
 
    def to_txt(self):
        return f"{self.username},{self.password},{self.rol}\n"
    
    def verificar_password(self, password):
        contador_num=0
        contador_caresp=0
        contador_mayusculas=0
        contador_minusculas=0
        
        for caracter in password:
            if caracter == " ":
                return False
            if caracter.isdigit():
                contador_num+=1
            if caracter.isalnum() == False:
                contador_caresp+=1
            if caracter.isupper():
                contador_mayusculas+=1
            if caracter.islower():
                contador_minusculas+=1
        
        if len(password)<8 or contador_num<2 or contador_caresp == 0 or contador_mayusculas==0 or contador_minusculas==0:
            return False