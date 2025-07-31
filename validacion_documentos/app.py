from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
DATABASE = 'documentos.db'

def crear_base_datos():
    if not os.path.exists(DATABASE):
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE documentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo TEXT UNIQUE,
                nombre_funcionario TEXT,
                tipo_documento TEXT,
                fecha_emision TEXT
            )
        ''')
        conn.commit()
        conn.close()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/emitir', methods=['GET', 'POST'])
def emitir():
    if request.method == 'POST':
        codigo = request.form['codigo']
        nombre_funcionario = request.form['nombre_funcionario']
        tipo_documento = request.form['tipo_documento']
        fecha_emision = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        try:
            conn = sqlite3.connect(DATABASE)
            c = conn.cursor()
            c.execute('INSERT INTO documentos (codigo, nombre_funcionario, tipo_documento, fecha_emision) VALUES (?,?,?,?)',
                      (codigo, nombre_funcionario, tipo_documento, fecha_emision))
            conn.commit()
            mensaje = "Documento emitido y registrado correctamente"
        except sqlite3.IntegrityError:
            mensaje = "El código ya existe"
        finally:
            conn.close()
        return render_template('home.html', mensaje=mensaje)
    return render_template('emitir.html')

@app.route('/validar', methods=['GET', 'POST'])
def validar():
    resultado = None
    if request.method == 'POST':
        codigo = request.form['codigo']
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute('SELECT nombre_funcionario, tipo_documento, fecha_emision FROM documentos WHERE codigo = ?', (codigo,))
        info = c.fetchone()
        conn.close()
        if info:
            resultado = {
                "valido": True,
                "nombre_funcionario": info[0],
                "tipo_documento": info[1],
                "fecha_emision": info[2]
            }
        else:
            resultado = {"valido": False}
        return render_template('resultado.html', resultado=resultado)
    return render_template('validar.html')

if __name__ == '__main__':
    crear_base_datos()
    app.run(debug=True)
