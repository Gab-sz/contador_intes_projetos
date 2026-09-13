"""Modulo de persistencia: cadastro de itens e historico de contagens.

Usa SQLite (ja vem no Python, sem precisar instalar nada nem configurar
servidor). O banco fica salvo num unico arquivo, por padrao
'contador_itens.db' na pasta onde o programa e executado.
"""

import sqlite3
from datetime import datetime


class BancoDados:
    """Encapsula todo o acesso ao SQLite. Ninguem fora desta classe deve
    escrever SQL diretamente -- a interface so chama estes metodos."""

    def __init__(self, caminho_bd="contador_itens.db"):
        self.caminho_bd = caminho_bd
        self._criar_tabelas()

    def _conectar(self):
        conexao = sqlite3.connect(self.caminho_bd)
        conexao.row_factory = sqlite3.Row
        return conexao

    def _criar_tabelas(self):
        with self._conectar() as conexao:
            conexao.execute(
                """
                CREATE TABLE IF NOT EXISTS itens (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    tipo TEXT,
                    criado_em TEXT NOT NULL
                )
                """
            )
            conexao.execute(
                """
                CREATE TABLE IF NOT EXISTS contagens (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    item_id INTEGER NOT NULL,
                    quantidade INTEGER NOT NULL,
                    data_hora TEXT NOT NULL,
                    FOREIGN KEY (item_id) REFERENCES itens (id)
                )
                """
            )

    # -- itens -----------------------------------------------------------

    def cadastrar_item(self, nome, tipo):
        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self._conectar() as conexao:
            cursor = conexao.execute(
                "INSERT INTO itens (nome, tipo, criado_em) VALUES (?, ?, ?)",
                (nome, tipo, agora),
            )
            return cursor.lastrowid

    def listar_itens(self):
        with self._conectar() as conexao:
            linhas = conexao.execute(
                "SELECT id, nome, tipo, criado_em FROM itens ORDER BY nome"
            ).fetchall()
            return [dict(linha) for linha in linhas]

    def buscar_item(self, item_id):
        with self._conectar() as conexao:
            linha = conexao.execute(
                "SELECT id, nome, tipo, criado_em FROM itens WHERE id = ?",
                (item_id,),
            ).fetchone()
            return dict(linha) if linha else None

    # -- contagens ---------------------------------------------------------

    def registrar_contagem(self, item_id, quantidade):
        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self._conectar() as conexao:
            conexao.execute(
                "INSERT INTO contagens (item_id, quantidade, data_hora) VALUES (?, ?, ?)",
                (item_id, quantidade, agora),
            )

    def historico_contagens(self, item_id):
        with self._conectar() as conexao:
            linhas = conexao.execute(
                "SELECT quantidade, data_hora FROM contagens "
                "WHERE item_id = ? ORDER BY data_hora DESC",
                (item_id,),
            ).fetchall()
            return [dict(linha) for linha in linhas]

    def total_contado(self, item_id):
        with self._conectar() as conexao:
            resultado = conexao.execute(
                "SELECT COALESCE(SUM(quantidade), 0) FROM contagens WHERE item_id = ?",
                (item_id,),
            ).fetchone()
            return resultado[0]
