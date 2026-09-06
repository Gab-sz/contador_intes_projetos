"""Modulo com o modelo de dados de um item sendo rastreado."""


class ObjetoRastreado:
    """Um item individual, do momento em que aparece no video ate sumir
    de cena. Guarda posicao atual/anterior e se ja foi contado."""

    def __init__(self, identificador, centro):
        self.identificador = identificador
        self.centro = centro
        self.centro_anterior = centro
        self.quadros_perdidos = 0
        self.contado = False

    def atualizar_posicao(self, novo_centro):
        self.centro_anterior = self.centro
        self.centro = novo_centro
        self.quadros_perdidos = 0

    def marcar_perdido(self):
        self.quadros_perdidos += 1

    def cruzou_linha(self, linha_y):
        """True se o objeto cruzou a linha horizontal 'linha_y' entre o
        quadro anterior e o atual, em qualquer sentido."""
        y_anterior = self.centro_anterior[1]
        y_atual = self.centro[1]
        return (y_anterior < linha_y <= y_atual) or (y_anterior > linha_y >= y_atual)
