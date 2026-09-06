# Contador de Itens - Esteira

Sistema de contagem automática de itens pequenos em esteira, usando visão computacional (OpenCV) e interface gráfica em customtkinter. 

## Como funciona

Uma câmera capta os itens passando pela esteira. O sistema detecta cada item em movimento e conta quando ele cruza uma linha virtual na tela — sem precisar reconhecer o item especificamente.

## Funcionalidades

- Interface gráfica com contador em tempo real
- Ajuste de sensibilidade e posição da linha de contagem
- Visualização da máscara de detecção (para calibrar)
- Histórico da sessão de contagem
- Exportação do registro em CSV

## Requisitos

- Python 3.10+
- Webcam

## Instalação

Baixe o projeto para o seu computador:

```bash
git clone https://github.com/Gab-sz/contador_intes_projetos.git
cd contador_intes_projetos
```

> `git clone` é usado só na primeira vez. Depois, para trazer atualizações do repositório, use `git pull` dentro da pasta do projeto.

Instale as dependências:

```bash
pip install opencv-python customtkinter pillow numpy
```

## Como executar

```bash
python main.py
```

## Estrutura do projeto

```
app/               -> interface gráfica (AplicativoContador)
Camera/            -> acesso à câmera (FonteCamera)
contador/          -> lógica de detecção e contagem (ContadorDeItens)
ObjetoRastreado/   -> modelo de um item rastreado
main.py            -> ponto de entrada
```