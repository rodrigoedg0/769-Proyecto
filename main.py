from src.controlador.sistema import Sistema
from src.vista.gui import App

def main():
    sistema = Sistema()
    app = App(sistema)
    app.run()

if __name__ == "__main__":
    main()