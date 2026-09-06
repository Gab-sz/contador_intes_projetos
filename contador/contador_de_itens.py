"""Modulo com a regra de negocio: deteccao, rastreamento e contagem."""

import cv2
import numpy as np
from datetime import datetime

from ObjetoRastreado.objeto_rastreado import ObjetoRastreado


class ContadorDeItens:
    """Toda a logica de visao computacional fica isolada aqui. A interface
    grafica so chama processar_quadro() e le a propriedade contagem."""

    def __init__(self, area_minima=300, distancia_maxima=60, max_quadros_perdidos=10):
        self.area_minima = area_minima
        self.distancia_maxima = distancia_maxima
        self.max_quadros_perdidos = max_quadros_perdidos
        self.proporcao_linha = 0.5  # posicao da linha (0.1 a 0.9 da altura do quadro)

        self._subtrator_fundo = cv2.createBackgroundSubtractorMOG2(
            history=300, varThreshold=40, detectShadows=False
        )
        self._objetos_rastreados = []
        self._proximo_id = 0
        self._contagem = 0
        self._registros = []

    @property
    def contagem(self):
        return self._contagem

    @property
    def registros(self):
        return list(self._registros)

    def reiniciar(self):
        self._contagem = 0
        self._objetos_rastreados = []
        self._registros = []

    def processar_quadro(self, quadro):
        """Recebe um quadro BGR (numpy array) e devolve o quadro anotado
        (com marcacoes, linha e contador desenhados)."""
        altura, largura = quadro.shape[:2]
        linha_y = int(altura * self.proporcao_linha)

        deteccoes = self._detectar_objetos(quadro)
        self._atualizar_rastreamento(deteccoes, linha_y)

        anotado = quadro.copy()
        for cx, cy in deteccoes:
            cv2.circle(anotado, (cx, cy), 6, (0, 255, 0), -1)
        cv2.line(anotado, (0, linha_y), (largura, linha_y), (0, 0, 255), 2)
        cv2.putText(
            anotado, f"Contagem: {self._contagem}", (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 0), 2
        )
        return anotado

    # -- metodos internos (prefixo _ = uso interno da classe) -----------

    def _detectar_objetos(self, quadro):
        mascara = self._subtrator_fundo.apply(quadro)
        _, mascara = cv2.threshold(mascara, 200, 255, cv2.THRESH_BINARY)
        mascara = cv2.morphologyEx(mascara, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
        mascara = cv2.dilate(mascara, np.ones((5, 5), np.uint8), iterations=2)

        contornos, _ = cv2.findContours(mascara, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        deteccoes = []
        for contorno in contornos:
            if cv2.contourArea(contorno) >= self.area_minima:
                x, y, largura_c, altura_c = cv2.boundingRect(contorno)
                deteccoes.append((x + largura_c // 2, y + altura_c // 2))
        return deteccoes

    def _atualizar_rastreamento(self, deteccoes, linha_y):
        nao_combinados = list(range(len(deteccoes)))

        # tenta casar cada objeto ja rastreado com a deteccao mais proxima
        for objeto in self._objetos_rastreados:
            indice_encontrado, menor_distancia = None, self.distancia_maxima
            for indice in nao_combinados:
                dx = objeto.centro[0] - deteccoes[indice][0]
                dy = objeto.centro[1] - deteccoes[indice][1]
                distancia = (dx ** 2 + dy ** 2) ** 0.5
                if distancia < menor_distancia:
                    menor_distancia, indice_encontrado = distancia, indice

            if indice_encontrado is not None:
                objeto.atualizar_posicao(deteccoes[indice_encontrado])
                nao_combinados.remove(indice_encontrado)
                if not objeto.contado and objeto.cruzou_linha(linha_y):
                    objeto.contado = True
                    self._contagem += 1
                    self._registros.append(datetime.now().strftime("%H:%M:%S"))
            else:
                objeto.marcar_perdido()

        # remove rastreamentos que sumiram ha muitos quadros
        self._objetos_rastreados = [
            o for o in self._objetos_rastreados if o.quadros_perdidos <= self.max_quadros_perdidos
        ]

        # cria novos rastreamentos para deteccoes que nao casaram com nada
        for indice in nao_combinados:
            self._objetos_rastreados.append(ObjetoRastreado(self._proximo_id, deteccoes[indice]))
            self._proximo_id += 1
