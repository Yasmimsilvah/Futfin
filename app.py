from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

def conectar():
    return sqlite3.connect('futfin.db')


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/dashboard')
def dashboard():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM gastos")
    dados = cursor.fetchall()

    cursor.execute("SELECT SUM(valor) FROM gastos WHERE tipo = 'receita'")
    receitas = cursor.fetchone()[0]
    if receitas is None:
        receitas = 0

    cursor.execute("SELECT SUM(valor) FROM gastos WHERE tipo = 'despesa'")
    despesas = cursor.fetchone()[0]
    if despesas is None:
        despesas = 0

    saldo = receitas - despesas

    receitas_formatadas = f"{receitas:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    despesas_formatadas = f"{despesas:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    saldo_formatado = f"{saldo:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    # Humor futebol
    if saldo > 0:
        humor = "vitória"
    elif saldo == 0:
        humor = "neutro"
    else:
        humor = "derrota"

    # Dados para gráfico
    categorias = []
    valores = []

    for g in dados:
        categorias.append(g[1])  # descrição
        valores.append(float(g[2]))

    conn.close()

    return render_template(
        'dashboard.html',
        gastos=dados,
        receitas=receitas_formatadas,
        despesas=despesas_formatadas,
        saldo=saldo_formatado,
        humor=humor,
        categorias=categorias,
        valores=valores
    )


@app.route('/add', methods=['POST'])
def add():
    descricao = request.form['descricao']
    valor = float(request.form['valor'])
    tipo = request.form['tipo']

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO gastos (descricao, valor, tipo) VALUES (?, ?, ?)",
        (descricao, valor, tipo)
    )

    conn.commit()
    conn.close()

    return redirect('/dashboard')


@app.route('/delete/<int:id>')
def delete(id):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM gastos WHERE id = ?", (id,))

    conn.commit()
    conn.close()

    return redirect('/dashboard')


if __name__ == '__main__':
    app.run(debug=True)