"""Modulo da interface grafica. Orquestra FonteCamera e ContadorDeItens."""

import cv2
import customtkinter as ctk
from PIL import Image, ImageTk
import csv
from datetime import datetime

from Camera.fonte_camera import FonteCamera
from contador.contador_de_itens import ContadorDeItens

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class AplicativoContador(ctk.CTk):
    """So cuida de janela, botoes e exibicao de video. Delega tudo de
    camera para FonteCamera e toda a logica de contagem para ContadorDeItens."""

    def __init__(self):
        super().__init__()
        self.title("Contador de Itens - Esteira")
        self.geometry("1000x720")
        self.minsize(900, 650)

        self._camera = FonteCamera()
        self._contador = ContadorDeItens()
        self._executando = False

        self._construir_interface()

    def _construir_interface(self):
        topo = ctk.CTkFrame(self)
        topo.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(topo, text="Fonte da camera:").pack(side="left", padx=5)
        self.campo_fonte = ctk.CTkEntry(
            topo, width=320,
            placeholder_text="0 (webcam) ou http://IP:8080/video (opcional)"
        )
        self.campo_fonte.insert(0, "0")
        self.campo_fonte.pack(side="left", padx=5)

        self.botao_conectar = ctk.CTkButton(topo, text="Conectar", command=self.conectar_camera)
        self.botao_conectar.pack(side="left", padx=5)

        self.botao_iniciar = ctk.CTkButton(
            topo, text="Iniciar contagem", command=self.alternar_execucao, state="disabled"
        )
        self.botao_iniciar.pack(side="left", padx=5)

        self.botao_zerar = ctk.CTkButton(topo, text="Zerar contador", command=self.zerar_contagem)
        self.botao_zerar.pack(side="left", padx=5)

        self.botao_salvar = ctk.CTkButton(topo, text="Salvar registro (CSV)", command=self.salvar_registro)
        self.botao_salvar.pack(side="left", padx=5)

        self.rotulo_video = ctk.CTkLabel(self, text="")
        self.rotulo_video.pack(padx=10, pady=5)

        quadro_contagem = ctk.CTkFrame(self)
        quadro_contagem.pack(fill="x", padx=10, pady=5)
        self.rotulo_contagem = ctk.CTkLabel(
            quadro_contagem, text="Contagem: 0", font=ctk.CTkFont(size=34, weight="bold")
        )
        self.rotulo_contagem.pack(side="left", padx=20, pady=10)

        ajustes = ctk.CTkFrame(self)
        ajustes.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(ajustes, text="Posicao da linha:").pack(side="left", padx=5)
        self.controle_linha = ctk.CTkSlider(ajustes, from_=0.1, to=0.9, command=self.atualizar_posicao_linha)
        self.controle_linha.set(0.5)
        self.controle_linha.pack(side="left", padx=5, fill="x", expand=True)

        ctk.CTkLabel(ajustes, text="Sensibilidade (area min.):").pack(side="left", padx=5)
        self.controle_area = ctk.CTkSlider(ajustes, from_=50, to=2000, command=self.atualizar_area_minima)
        self.controle_area.set(300)
        self.controle_area.pack(side="left", padx=5, fill="x", expand=True)

        self.rotulo_status = ctk.CTkLabel(self, text="Status: aguardando conexao com a camera")
        self.rotulo_status.pack(padx=10, pady=5)

    # -- eventos da interface, cada um delega para a classe responsavel --

    def conectar_camera(self):
        fonte = self.campo_fonte.get().strip()
        if self._camera.conectar(fonte):
            self.rotulo_status.configure(text="Status: camera conectada")
            self.botao_iniciar.configure(state="normal")
        else:
            self.rotulo_status.configure(text="Status: nao foi possivel conectar a fonte informada")
            self.botao_iniciar.configure(state="disabled")

    def alternar_execucao(self):
        self._executando = not self._executando
        self.botao_iniciar.configure(text="Pausar contagem" if self._executando else "Iniciar contagem")
        if self._executando:
            self._laco_atualizacao()

    def zerar_contagem(self):
        self._contador.reiniciar()
        self.rotulo_contagem.configure(text="Contagem: 0")

    def salvar_registro(self):
        nome_arquivo = f"contagem_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        with open(nome_arquivo, "w", newline="", encoding="utf-8") as arquivo:
            escritor = csv.writer(arquivo)
            escritor.writerow(["item_numero", "horario"])
            for numero, horario in enumerate(self._contador.registros, start=1):
                escritor.writerow([numero, horario])
            escritor.writerow([])
            escritor.writerow(["total", self._contador.contagem])
        self.rotulo_status.configure(text=f"Status: registro salvo em {nome_arquivo}")

    def atualizar_posicao_linha(self, valor):
        self._contador.proporcao_linha = float(valor)

    def atualizar_area_minima(self, valor):
        self._contador.area_minima = float(valor)

    def _laco_atualizacao(self):
        if not self._executando:
            return

        sucesso, quadro = self._camera.ler_quadro()
        if not sucesso:
            self.rotulo_status.configure(text="Status: sinal da camera perdido")
            self._executando = False
            self.botao_iniciar.configure(text="Iniciar contagem")
            return

        quadro = cv2.resize(quadro, (720, 480))
        anotado = self._contador.processar_quadro(quadro)

        quadro_rgb = cv2.cvtColor(anotado, cv2.COLOR_BGR2RGB)
        imagem = Image.fromarray(quadro_rgb)
        imagem_tk = ImageTk.PhotoImage(image=imagem)
        self.rotulo_video.configure(image=imagem_tk)
        self.rotulo_video.image = imagem_tk

        self.rotulo_contagem.configure(text=f"Contagem: {self._contador.contagem}")
        self.after(20, self._laco_atualizacao)

    def ao_fechar(self):
        self._executando = False
        self._camera.liberar()
        self.destroy()
