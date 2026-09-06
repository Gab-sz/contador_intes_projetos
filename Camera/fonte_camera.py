"""Modulo responsavel exclusivamente pelo acesso a camera."""

import cv2


class FonteCamera:
    

    def __init__(self):
        self._captura = None

    @property
    def esta_conectada(self):
        return self._captura is not None and self._captura.isOpened()

    def conectar(self, fonte):
       
        self.liberar()
        try:
            fonte = int(fonte)
        except ValueError:
            pass  
        self._captura = cv2.VideoCapture(fonte)
        return self.esta_conectada

    def ler_quadro(self):
        if not self.esta_conectada:
            return False, None
        return self._captura.read()

    def liberar(self):
        if self._captura is not None:
            self._captura.release()
            self._captura = None
