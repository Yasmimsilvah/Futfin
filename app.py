from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "futfin_chave_secreta"


def conectar():
    return sqlite3.connect('futfin.db')

@app.route('/')
def home():
    return redirect('/login')


# ==========================
# CADASTRO
# ==========================
@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():

    if request.method == 'POST':

        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']

        conn = conectar()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO usuarios (nome, email, senha)
                VALUES (?, ?, ?)
                """,
                (nome, email, senha)
            )

            conn.commit()

        except sqlite3.IntegrityError:
            conn.close()
            return "Email já cadastrado."

        conn.close()

        return redirect('/login')

    return render_template('cadastro.html')


# ==========================
# LOGIN
# ==========================
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']
        senha = request.form['senha']

        conn = conectar()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT * FROM usuarios
            WHERE email = ? AND senha = ?
            """,
            (email, senha)
        )

        usuario = cursor.fetchone()
       
        print(usuario)

        conn.close()

        if usuario:

            session['usuario_id'] = usuario[0]
            session['usuario_nome'] = usuario[1]

            return redirect('/dashboard')

        return "Email ou senha inválidos."

    return render_template('login.html')


# ==========================
# LOGOUT
# ==========================
@app.route('/logout')
def logout():

    session.clear()

    return redirect('/login')


# ==========================
# DASHBOARD
# ==========================
@app.route('/dashboard')
def dashboard():

    if 'usuario_id' not in session:
        return redirect('/login')

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM gastos")
    dados = cursor.fetchall()

    cursor.execute(
        "SELECT SUM(valor) FROM gastos WHERE tipo='receita'"
    )
    receitas = cursor.fetchone()[0] or 0

    cursor.execute(
        "SELECT SUM(valor) FROM gastos WHERE tipo='despesa'"
    )
    despesas = cursor.fetchone()[0] or 0

    saldo = receitas - despesas

    receitas_formatadas = (
        f"{receitas:,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )

    despesas_formatadas = (
        f"{despesas:,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )

    saldo_formatado = (
        f"{saldo:,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )

    if saldo > 0:
        humor = "vitória"
    elif saldo == 0:
        humor = "neutro"
    else:
        humor = "derrota"

    categorias = []
    valores = []

    for g in dados:
        categorias.append(g[1])
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
        valores=valores,
        usuario=session['usuario_nome']
    )


# ==========================
# ADICIONAR GASTO
# ==========================
@app.route('/add', methods=['POST'])
def add():

    if 'usuario_id' not in session:
        return redirect('/login')

    descricao = request.form['descricao']
    valor = float(request.form['valor'])
    tipo = request.form['tipo']

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO gastos
        (descricao, valor, tipo)
        VALUES (?, ?, ?)
        """,
        (descricao, valor, tipo)
    )

    conn.commit()
    conn.close()

    return redirect('/dashboard')


# ==========================
# EXCLUIR GASTO
# ==========================
@app.route('/delete/<int:id>')
def delete(id):

    if 'usuario_id' not in session:
        return redirect('/login')

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM gastos WHERE id = ?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect('/dashboard')

print("APP COM LOGIN CARREGADO")

if __name__ == '__main__':
    app.run(debug=True)