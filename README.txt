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

IMPORTANTE sobre os imports:
    Como agora cada classe mora numa pasta diferente, os imports usam o
    caminho completo, por exemplo:

        from Camera.fonte_camera import FonteCamera
        from contador.contador_de_itens import ContadorDeItens
        from ObjetoRastreado.objeto_rastreado import ObjetoRastreado

    O arquivo __init__.py vazio dentro de cada pasta e o que diz ao Python
    "esta pasta e um pacote, pode importar coisas de dentro dela".

    Os nomes das pastas (Camera, ObjetoRastreado) tem letra maiuscula no
    inicio. Isso funciona normalmente no Windows, mas em Linux/Mac o
    Python DIFERENCIA maiusculas de minusculas nos imports -- entao o
    nome da pasta e o nome usado no import precisam ser identicos, letra
    por letra, nos dois sistemas.
