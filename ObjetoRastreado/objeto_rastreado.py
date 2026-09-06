"""Modulo com o modelo de dados de um item sendo rastreado."""


class ObjetoRastreado:
    """Um item individual, do momento em que aparece no video ate sumir
    de cena.

    Em vez de comparar so a posicao do quadro anterior com a atual (o que
    e sensivel a tremor/ruido bem em cima da linha), este objeto guarda um
    "lado confirmado" da linha. Esse lado so muda quando o item sai
    claramente da zona de seguranca em volta da linha -- pequenas
    oscilacoes dentro dessa zona nao contam como cruzamento.
    """

    def __init__(self, identificador, centro):
        self.identificador = identificador
        self.centro = centro
        self.quadros_perdidos = 0
        self.contado = False
        self.lado_confirmado = None  # 'acima', 'abaixo' ou None (ainda indefinido)

    def atualizar_posicao(self, novo_centro):
        self.centro = novo_centro
        self.quadros_perdidos = 0

    def marcar_perdido(self):
        self.quadros_perdidos += 1

    def lado_da_linha(self, linha_y, margem_seguranca):
        """Retorna 'acima', 'abaixo', ou None se o centro estiver dentro
        da zona de seguranca (perto demais da linha para ter certeza do lado)."""
        y = self.centro[1]
        if y < linha_y - margem_seguranca:
            return "acima"
        if y > linha_y + margem_seguranca:
            return "abaixo"
        return None
