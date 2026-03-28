from src.controlador.sistema import Sistema
from src.vista.consola import Consola

def main():
    sistema = Sistema()
    consola = Consola(sistema)
    consola.iniciar()

if __name__ == "__main__":
    main()