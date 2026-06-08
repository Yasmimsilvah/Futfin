import sqlite3

def conectar():
    return sqlite3.connect('futfin.db')


def criar_tabela():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS gastos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        descricao TEXT NOT NULL,
        valor REAL NOT NULL,
        tipo TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()

criar_tabela()