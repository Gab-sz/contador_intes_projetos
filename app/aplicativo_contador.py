"""Modulo da interface grafica. Orquestra FonteCamera e ContadorDeItens."""

import time
import cv2
import customtkinter as ctk
from PIL import Image
import csv
from datetime import datetime

from Camera.fonte_camera import FonteCamera
from contador.contador_de_itens import ContadorDeItens

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

COR_STATUS_OK = "#2ecc71"
COR_STATUS_ERRO = "#e74c3c"
COR_STATUS_NEUTRO = "#7f8c8d"


class AplicativoContador(ctk.CTk):
    """So cuida de janela, layout e eventos da interface. Delega tudo de
    camera para FonteCamera e toda a logica de contagem para ContadorDeItens."""

    def __init__(self):
        super().__init__()
        self.title("Contador de Itens - Esteira")
        self.geometry("1180x760")
        self.minsize(1000, 640)

        self._camera = FonteCamera()
        self._contador = ContadorDeItens()
        self._executando = False
        self._mostrar_mascara = False
        self._ultimo_tempo_quadro = None
        self._fps_atual = 0.0

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._construir_barra_lateral()
        self._construir_area_principal()

    # ------------------------------------------------------------------ #
    # Construcao da interface
    # ------------------------------------------------------------------ #

    def _construir_barra_lateral(self):
        barra = ctk.CTkFrame(self, width=300, corner_radius=0)
        barra.grid(row=0, column=0, sticky="nsw")
        barra.grid_propagate(False)
        barra.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            barra, text="Contador de Itens",
            font=ctk.CTkFont(size=20, weight="bold")
        ).grid(row=0, column=0, padx=16, pady=(20, 4), sticky="w")

        # area rolavel com todas as secoes de controle
        conteudo = ctk.CTkScrollableFrame(barra, fg_color="transparent")
        conteudo.grid(row=1, column=0, sticky="nsew")
        conteudo.grid_columnconfigure(0, weight=1)

        # -- secao: camera ------------------------------------------------
        secao_camera = self._criar_secao(conteudo, "CAMERA")

        self.campo_fonte = ctk.CTkEntry(
            secao_camera, placeholder_text="0 (webcam) ou URL"
        )
        self.campo_fonte.insert(0, "0")
        self.campo_fonte.pack(fill="x", padx=4, pady=(4, 6))

        self.botao_conectar = ctk.CTkButton(
            secao_camera, text="Conectar", command=self.conectar_camera
        )
        self.botao_conectar.pack(fill="x", padx=4, pady=(0, 6))

        linha_status = ctk.CTkFrame(secao_camera, fg_color="transparent")
        linha_status.pack(fill="x", padx=4, pady=(0, 4))
        self.indicador_status = ctk.CTkLabel(
            linha_status, text="●", text_color=COR_STATUS_NEUTRO,
            font=ctk.CTkFont(size=16)
        )
        self.indicador_status.pack(side="left")
        self.rotulo_status = ctk.CTkLabel(
            linha_status, text="Aguardando conexao", font=ctk.CTkFont(size=12)
        )
        self.rotulo_status.pack(side="left", padx=(6, 0))

        self.rotulo_fps = ctk.CTkLabel(
            secao_camera, text="FPS: --", font=ctk.CTkFont(size=12), text_color="gray60"
        )
        self.rotulo_fps.pack(anchor="w", padx=4, pady=(0, 4))

        # -- secao: controles ----------------------------------------------
        secao_controles = self._criar_secao(conteudo, "CONTROLES")

        self.botao_iniciar = ctk.CTkButton(
            secao_controles, text="▶  Iniciar contagem",
            command=self.alternar_execucao, state="disabled",
            fg_color="#2b8a3e", hover_color="#237032"
        )
        self.botao_iniciar.pack(fill="x", padx=4, pady=(4, 6))

        linha_botoes = ctk.CTkFrame(secao_controles, fg_color="transparent")
        linha_botoes.pack(fill="x", padx=4)
        linha_botoes.grid_columnconfigure((0, 1), weight=1)

        self.botao_zerar = ctk.CTkButton(
            linha_botoes, text="Zerar", command=self.zerar_contagem,
            fg_color="#8a2b2b", hover_color="#702323"
        )
        self.botao_zerar.grid(row=0, column=0, sticky="ew", padx=(0, 3))

        self.botao_salvar = ctk.CTkButton(
            linha_botoes, text="Salvar CSV", command=self.salvar_registro
        )
        self.botao_salvar.grid(row=0, column=1, sticky="ew", padx=(3, 0))

        # -- secao: deteccao basica -----------------------------------------
        secao_deteccao = self._criar_secao(conteudo, "DETECCAO")

        self.rotulo_linha = ctk.CTkLabel(secao_deteccao, text="Posicao da linha: 50%")
        self.rotulo_linha.pack(anchor="w", padx=4)
        self.controle_linha = ctk.CTkSlider(
            secao_deteccao, from_=0.1, to=0.9, command=self.atualizar_posicao_linha
        )
        self.controle_linha.set(0.5)
        self.controle_linha.pack(fill="x", padx=4, pady=(0, 10))

        self.rotulo_area = ctk.CTkLabel(secao_deteccao, text="Sensibilidade (area min.): 300")
        self.rotulo_area.pack(anchor="w", padx=4)
        self.controle_area = ctk.CTkSlider(
            secao_deteccao, from_=50, to=2000, command=self.atualizar_area_minima
        )
        self.controle_area.set(300)
        self.controle_area.pack(fill="x", padx=4, pady=(0, 6))

        self.interruptor_mascara = ctk.CTkSwitch(
            secao_deteccao, text="Ver mascara de deteccao",
            command=self.alternar_mascara
        )
        self.interruptor_mascara.pack(anchor="w", padx=4, pady=(6, 4))

        # -- secao: calibracao de velocidade / rastreamento ------------------
        secao_velocidade = self._criar_secao(conteudo, "CALIBRACAO DE VELOCIDADE")
        ctk.CTkLabel(
            secao_velocidade,
            text="Ajuste conforme a webcam e a velocidade real dos itens.",
            font=ctk.CTkFont(size=11), text_color="gray60", wraplength=230, justify="left"
        ).pack(anchor="w", padx=4, pady=(0, 8))

        self.rotulo_margem = ctk.CTkLabel(
            secao_velocidade, text="Zona de seguranca da linha: 15px"
        )
        self.rotulo_margem.pack(anchor="w", padx=4)
        self.controle_margem = ctk.CTkSlider(
            secao_velocidade, from_=5, to=60, number_of_steps=55,
            command=self.atualizar_margem_seguranca
        )
        self.controle_margem.set(15)
        self.controle_margem.pack(fill="x", padx=4, pady=(0, 10))

        self.rotulo_distancia = ctk.CTkLabel(
            secao_velocidade, text="Tolerancia de deslocamento: 60px"
        )
        self.rotulo_distancia.pack(anchor="w", padx=4)
        self.controle_distancia = ctk.CTkSlider(
            secao_velocidade, from_=10, to=200, number_of_steps=190,
            command=self.atualizar_distancia_maxima
        )
        self.controle_distancia.set(60)
        self.controle_distancia.pack(fill="x", padx=4, pady=(0, 10))

        self.rotulo_oclusao = ctk.CTkLabel(
            secao_velocidade, text="Tolerancia de oclusao: 10 quadros"
        )
        self.rotulo_oclusao.pack(anchor="w", padx=4)
        self.controle_oclusao = ctk.CTkSlider(
            secao_velocidade, from_=2, to=30, number_of_steps=28,
            command=self.atualizar_tolerancia_oclusao
        )
        self.controle_oclusao.set(10)
        self.controle_oclusao.pack(fill="x", padx=4, pady=(0, 6))

        # -- rodape: aparencia -------------------------------------------
        rodape = ctk.CTkFrame(barra, fg_color="transparent")
        rodape.grid(row=2, column=0, sticky="ew", padx=16, pady=16)
        ctk.CTkLabel(rodape, text="Tema:", font=ctk.CTkFont(size=12)).pack(side="left")
        self.interruptor_tema = ctk.CTkSwitch(
            rodape, text="Claro", command=self.alternar_tema
        )
        self.interruptor_tema.pack(side="left", padx=8)

    def _criar_secao(self, pai, titulo):
        """Cria um bloco com titulo dentro da barra lateral, retorna o
        frame onde os widgets daquela secao devem ser colocados."""
        ctk.CTkLabel(
            pai, text=titulo, font=ctk.CTkFont(size=11, weight="bold"),
            text_color="gray50"
        ).pack(anchor="w", padx=4, pady=(10, 2))
        secao = ctk.CTkFrame(pai, fg_color="transparent")
        secao.pack(fill="x", padx=0, pady=(0, 4))
        return secao

    def _construir_area_principal(self):
        principal = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        principal.grid(row=0, column=1, sticky="nsew", padx=16, pady=16)
        principal.grid_rowconfigure(0, weight=1)
        principal.grid_columnconfigure(0, weight=1)

        self.abas = ctk.CTkTabview(principal)
        self.abas.grid(row=0, column=0, sticky="nsew")
        aba_ao_vivo = self.abas.add("Ao vivo")
        aba_historico = self.abas.add("Historico")

        # -- aba "Ao vivo" -------------------------------------------------
        aba_ao_vivo.grid_columnconfigure(0, weight=1)
        aba_ao_vivo.grid_rowconfigure(0, weight=1)

        moldura_video = ctk.CTkFrame(aba_ao_vivo, fg_color="#111111")
        moldura_video.grid(row=0, column=0, sticky="nsew", pady=(4, 12))
        self.rotulo_video = ctk.CTkLabel(moldura_video, text="Conecte uma camera para comecar")
        self.rotulo_video.pack(expand=True, padx=8, pady=8)

        barra_contagem = ctk.CTkFrame(aba_ao_vivo)
        barra_contagem.grid(row=1, column=0, sticky="ew")
        barra_contagem.grid_columnconfigure(0, weight=1)

        self.rotulo_contagem = ctk.CTkLabel(
            barra_contagem, text="0", font=ctk.CTkFont(size=48, weight="bold")
        )
        self.rotulo_contagem.grid(row=0, column=0, sticky="w", padx=20, pady=10)

        ctk.CTkLabel(
            barra_contagem, text="itens contados", font=ctk.CTkFont(size=13),
            text_color="gray60"
        ).grid(row=0, column=1, sticky="w")

        self.rotulo_ultima = ctk.CTkLabel(
            barra_contagem, text="Ultima contagem: --:--:--",
            font=ctk.CTkFont(size=13), text_color="gray60"
        )
        self.rotulo_ultima.grid(row=0, column=2, sticky="e", padx=20)
        barra_contagem.grid_columnconfigure(2, weight=1)

        # -- aba "Historico" -------------------------------------------------
        aba_historico.grid_columnconfigure(0, weight=1)
        aba_historico.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            aba_historico, text="Registro de itens contados nesta sessao",
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=0, column=0, sticky="w", pady=(4, 8))

        self.lista_historico = ctk.CTkScrollableFrame(aba_historico)
        self.lista_historico.grid(row=1, column=0, sticky="nsew")
        self.lista_historico.grid_columnconfigure(0, weight=1)

    # ------------------------------------------------------------------ #
    # Eventos - cada um delega para a classe responsavel
    # ------------------------------------------------------------------ #

    def conectar_camera(self):
        fonte = self.campo_fonte.get().strip()
        if self._camera.conectar(fonte):
            self._definir_status("Camera conectada", COR_STATUS_OK)
            self.botao_iniciar.configure(state="normal")
        else:
            self._definir_status("Falha ao conectar", COR_STATUS_ERRO)
            self.botao_iniciar.configure(state="disabled")

    def _definir_status(self, texto, cor):
        self.indicador_status.configure(text_color=cor)
        self.rotulo_status.configure(text=texto)

    def alternar_execucao(self):
        self._executando = not self._executando
        if self._executando:
            self.botao_iniciar.configure(text="⏸  Pausar contagem", fg_color="#b5860b", hover_color="#96700a")
            self._ultimo_tempo_quadro = None
            self._laco_atualizacao()
        else:
            self.botao_iniciar.configure(text="▶  Iniciar contagem", fg_color="#2b8a3e", hover_color="#237032")

    def zerar_contagem(self):
        self._contador.reiniciar()
        self.rotulo_contagem.configure(text="0")
        self.rotulo_ultima.configure(text="Ultima contagem: --:--:--")
        for widget in self.lista_historico.winfo_children():
            widget.destroy()

    def salvar_registro(self):
        nome_arquivo = f"contagem_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        with open(nome_arquivo, "w", newline="", encoding="utf-8") as arquivo:
            escritor = csv.writer(arquivo)
            escritor.writerow(["item_numero", "horario"])
            for numero, horario in enumerate(self._contador.registros, start=1):
                escritor.writerow([numero, horario])
            escritor.writerow([])
            escritor.writerow(["total", self._contador.contagem])
        self._definir_status(f"Registro salvo: {nome_arquivo}", COR_STATUS_OK)

    def atualizar_posicao_linha(self, valor):
        self._contador.proporcao_linha = float(valor)
        self.rotulo_linha.configure(text=f"Posicao da linha: {int(float(valor) * 100)}%")

    def atualizar_area_minima(self, valor):
        self._contador.area_minima = float(valor)
        self.rotulo_area.configure(text=f"Sensibilidade (area min.): {int(float(valor))}")

    def atualizar_margem_seguranca(self, valor):
        self._contador.margem_seguranca = int(float(valor))
        self.rotulo_margem.configure(text=f"Zona de seguranca da linha: {int(float(valor))}px")

    def atualizar_distancia_maxima(self, valor):
        self._contador.distancia_maxima = float(valor)
        self.rotulo_distancia.configure(text=f"Tolerancia de deslocamento: {int(float(valor))}px")

    def atualizar_tolerancia_oclusao(self, valor):
        self._contador.max_quadros_perdidos = int(float(valor))
        self.rotulo_oclusao.configure(text=f"Tolerancia de oclusao: {int(float(valor))} quadros")

    def alternar_mascara(self):
        self._mostrar_mascara = bool(self.interruptor_mascara.get())

    def alternar_tema(self):
        claro = bool(self.interruptor_tema.get())
        ctk.set_appearance_mode("light" if claro else "dark")

    def _adicionar_item_historico(self, numero, horario):
        linha = ctk.CTkFrame(self.lista_historico, fg_color="transparent")
        linha.grid(row=numero - 1, column=0, sticky="ew", pady=2)
        linha.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(linha, text=f"#{numero}", width=50, anchor="w").grid(row=0, column=0)
        ctk.CTkLabel(linha, text="item contado", anchor="w").grid(row=0, column=1, sticky="w")
        ctk.CTkLabel(linha, text=horario, text_color="gray60").grid(row=0, column=2, padx=8)

    def _atualizar_fps(self):
        agora = time.time()
        if self._ultimo_tempo_quadro is not None:
            delta = agora - self._ultimo_tempo_quadro
            if delta > 0:
                fps_instantaneo = 1.0 / delta
                # suavizacao exponencial para o numero nao "tremer" na tela
                self._fps_atual = self._fps_atual * 0.9 + fps_instantaneo * 0.1
                self.rotulo_fps.configure(text=f"FPS: {self._fps_atual:.1f}")
        self._ultimo_tempo_quadro = agora

    def _laco_atualizacao(self):
        if not self._executando:
            return

        sucesso, quadro = self._camera.ler_quadro()
        if not sucesso:
            self._definir_status("Sinal da camera perdido", COR_STATUS_ERRO)
            self._executando = False
            self.botao_iniciar.configure(text="▶  Iniciar contagem", fg_color="#2b8a3e", hover_color="#237032")
            return

        self._atualizar_fps()

        quadro = cv2.resize(quadro, (760, 480))
        contagem_antes = self._contador.contagem
        anotado = self._contador.processar_quadro(quadro)

        if self._mostrar_mascara and self._contador.ultima_mascara is not None:
            imagem_exibida = cv2.cvtColor(self._contador.ultima_mascara, cv2.COLOR_GRAY2RGB)
        else:
            imagem_exibida = cv2.cvtColor(anotado, cv2.COLOR_BGR2RGB)

        imagem = Image.fromarray(imagem_exibida)
        imagem_ctk = ctk.CTkImage(light_image=imagem, dark_image=imagem, size=(760, 480))
        self.rotulo_video.configure(image=imagem_ctk, text="")
        self.rotulo_video.image = imagem_ctk

        nova_contagem = self._contador.contagem
        self.rotulo_contagem.configure(text=str(nova_contagem))

        if nova_contagem > contagem_antes:
            horario = self._contador.registros[-1]
            self.rotulo_ultima.configure(text=f"Ultima contagem: {horario}")
            self._adicionar_item_historico(nova_contagem, horario)

        self.after(20, self._laco_atualizacao)

    def ao_fechar(self):
        self._executando = False
        self._camera.liberar()
        self.destroy()
