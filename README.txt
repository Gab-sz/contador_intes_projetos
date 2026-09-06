CONTADOR DE ITENS - ESTEIRA (estrutura em pastas)
====================================================

Estrutura do projeto:

    app/
        __init__.py
        aplicativo_contador.py   -> classe AplicativoContador (interface grafica)
    Camera/
        __init__.py
        fonte_camera.py          -> classe FonteCamera (acesso a webcam/camera)
    contador/
        __init__.py
        contador_de_itens.py     -> classe ContadorDeItens (deteccao/rastreamento/contagem)
    ObjetoRastreado/
        __init__.py
        objeto_rastreado.py      -> classe ObjetoRastreado (modelo de um item)
    main.py                      -> ponto de entrada; roda a partir da RAIZ do projeto
    README.txt

Instalacao (uma vez so):
    pip install opencv-python customtkinter pillow numpy

Como executar:
    1. Abra o terminal na pasta RAIZ do projeto (onde fica main.py)
    2. Rode: python main.py

