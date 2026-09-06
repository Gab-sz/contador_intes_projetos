"""Modulo responsavel exclusivamente pelo acesso a camera."""

import cv2


class FonteCamera:
    """Encapsula o cv2.VideoCapture. Ninguem fora desta classe precisa
    saber como o OpenCV abre uma webcam ou uma URL de camera IP."""

    def __init__(self):
        self._captura = None

    @property
    def esta_conectada(self):
        return self._captura is not None and self._captura.isOpened()

    def conectar(self, fonte):
        """Aceita indice de webcam (0, 1, 2...) ou uma URL de camera IP."""
        self.liberar()
        try:
            fonte = int(fonte)
        except ValueError:
            pass  # era mesmo uma URL/string
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
