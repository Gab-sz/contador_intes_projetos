"""Ponto de entrada do programa. So cria e inicia a aplicacao."""

from app.aplicativo_contador import AplicativoContador


def main():
    aplicativo = AplicativoContador()
    aplicativo.protocol("WM_DELETE_WINDOW", aplicativo.ao_fechar)
    aplicativo.mainloop()


if __name__ == "__main__":
    main()
