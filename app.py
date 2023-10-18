from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = "conalep253"

@app.route('/')
def root():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        usuario = request.form['usuario']
        password = request.form['password']

        conn = sqlite3.connect('escuela.db')
        c = conn.cursor()

        c.execute("SELECT * FROM usuarios WHERE usuario = ? AND password = ?", (usuario, password))
        user = c.fetchone()
        session['usuario'] = usuario

        conn.close()

        if user is None:
            error = 'Usuario o contraseña incorrectos'
        else:
            return redirect(url_for('reciente'))

    return render_template('login.html', error=error)

@app.route('/busqueda', methods=['GET', 'POST'])
def busqueda():
    if request.method == 'POST':
        consulta = request.form['consulta']

        conn = sqlite3.connect('escuela.db')
        c = conn.cursor()

        c.execute("SELECT datos_alumno.*, COUNT(comentarios.matricula) as num_comentarios FROM datos_alumno LEFT JOIN comentarios ON datos_alumno.matricula = comentarios.matricula WHERE datos_alumno.matricula LIKE ? OR nombre LIKE ? OR apepat LIKE ? OR apemat LIKE ? GROUP BY datos_alumno.matricula",
                  ('%' + consulta + '%', '%' + consulta + '%', '%' + consulta + '%', '%' + consulta + '%'))
        
        resultados = c.fetchall()

        # Almacena los resultados en la sesión del usuario
        session['resultados'] = resultados

        conn.close()

        return render_template('resultados.html', resultados=resultados)

    return render_template('busqueda.html')


@app.route('/ficha/<matricula>', methods=['GET'])
def ficha(matricula):
    conn = sqlite3.connect('escuela.db')
    c = conn.cursor()

    c.execute("SELECT * FROM datos_alumno WHERE matricula = ?", (matricula,))
    alumno = c.fetchone()

    c.execute("SELECT * FROM comentarios WHERE matricula = ? ORDER BY fecha DESC", (matricula,))
    comentarios = c.fetchall()

    conn.close()

    if alumno is None:
        return 'No se encontró al alumno', 404
    
    # Elimina la variable de la sesión si está establecida
    session.pop('form_submitted', None)

    return render_template('ficha.html', alumno=alumno, comentarios=comentarios)

@app.route('/guardar_comentario/<matricula>', methods=['POST'])
def guardar_comentario(matricula):
    usuario = session.get('usuario') #aqui se obtiene el nombre de usuario de la session
    #usuario = request.form['usuario']  # Aquí debes obtener el nombre de usuario de alguna manera
    comentario = request.form['comentario']

    conn = sqlite3.connect('escuela.db')
    c = conn.cursor()

    c.execute("INSERT INTO comentarios (matricula, fecha, comentario, usuario) VALUES (?, date('now'), ?, ?)", (matricula, comentario, usuario))

    conn.commit()
    conn.close()
    
    # Establece una variable en la sesión del usuario para indicar que se ha enviado el formulario
    session['form_submitted'] = True

    return redirect(url_for('ficha', matricula=matricula))

@app.route('/resultados')
def resultados():
    ordenar = request.args.get('ordenar', 'matricula')  # El valor predeterminado es 'matricula'

    # Obtiene los resultados de la sesión del usuario
    resultados = session.get('resultados', [])

    # Ordena los resultados
    if ordenar == 'matricula':
        resultados.sort(key=lambda x: x[0])
    elif ordenar == 'grupo':
        resultados.sort(key=lambda x: x[1])
    elif ordenar == 'nombre':
        resultados.sort(key=lambda x: x[2])
    elif ordenar == 'apepat':
        resultados.sort(key=lambda x: x[3])
    elif ordenar == 'apemat':
        resultados.sort(key=lambda x: x[4])


    return render_template('resultados.html', resultados=resultados)


@app.route('/logout', methods=['GET','POST'])
def logout():
    session.pop('usuario', None)
    return redirect(url_for('login'))

@app.route('/reporte', methods=['GET', 'POST'])
def reporte():
    conn = sqlite3.connect('escuela.db')
    c = conn.cursor()

    if request.method == 'POST':
        criterio = request.form['criterio']

        if criterio == 'amarillo':
            # Buscar registros con 1-5 comentarios
            c.execute("SELECT datos_alumno.matricula, datos_alumno.nombre, datos_alumno.apepat, datos_alumno.apemat, COUNT(*) as num_comentarios FROM comentarios INNER JOIN datos_alumno ON comentarios.matricula = datos_alumno.matricula GROUP BY comentarios.matricula HAVING num_comentarios BETWEEN 1 AND 5 ORDER BY num_comentarios DESC")
        elif criterio == 'rojo':
            # Buscar registros con más de 10 comentarios
            c.execute("SELECT datos_alumno.matricula, datos_alumno.nombre, datos_alumno.apepat, datos_alumno.apemat, COUNT(*) as num_comentarios FROM comentarios INNER JOIN datos_alumno ON comentarios.matricula = datos_alumno.matricula GROUP BY comentarios.matricula HAVING num_comentarios > 10 ORDER BY num_comentarios DESC")
        elif criterio == 'semana':
            # Buscar registros de la última semana
            c.execute("SELECT datos_alumno.matricula, datos_alumno.nombre, datos_alumno.apepat, datos_alumno.apemat, COUNT(*) as num_comentarios FROM comentarios INNER JOIN datos_alumno ON comentarios.matricula = datos_alumno.matricula WHERE fecha >= date('now','-7 day') GROUP BY comentarios.matricula ORDER BY num_comentarios DESC")
        elif criterio == 'mes':
            # Buscar registros del último mes
            c.execute("SELECT datos_alumno.matricula, datos_alumno.nombre, datos_alumno.apepat, datos_alumno.apemat, COUNT(*) as num_comentarios FROM comentarios INNER JOIN datos_alumno ON comentarios.matricula = datos_alumno.matricula WHERE fecha >= date('now','-1 month') GROUP BY comentarios.matricula ORDER BY num_comentarios DESC")
        elif criterio == 'todos':
            # Buscar todos los registros
            c.execute("SELECT datos_alumno.matricula, datos_alumno.nombre, datos_alumno.apepat, datos_alumno.apemat, COUNT(*) as num_comentarios FROM comentarios INNER JOIN datos_alumno ON comentarios.matricula = datos_alumno.matricula GROUP BY comentarios.matricula ORDER BY num_comentarios DESC")
        elif criterio == 'rango':
            fecha_inicio = request.form['fecha_inicio']
            fecha_fin = request.form['fecha_fin']
            # Buscar registros entre fecha_inicio y fecha_fin
            c.execute("SELECT datos_alumno.matricula, datos_alumno.nombre, datos_alumno.apepat, datos_alumno.apemat, COUNT(*) as num_comentarios FROM comentarios INNER JOIN datos_alumno ON comentarios.matricula = datos_alumno.matricula WHERE fecha BETWEEN ? AND ? GROUP BY comentarios.matricula ORDER BY num_comentarios DESC", (fecha_inicio, fecha_fin))

    # Si no se envió un formulario o si el criterio no es válido, muestra todos los registros
    else:
        c.execute("SELECT datos_alumno.matricula, datos_alumno.nombre, datos_alumno.apepat, datos_alumno.apemat, COUNT(*) as num_comentarios FROM comentarios INNER JOIN datos_alumno ON comentarios.matricula = datos_alumno.matricula GROUP BY comentarios.matricula ORDER BY num_comentarios DESC")

    registros = c.fetchall()

    conn.close()

    return render_template('reporte.html', registros=registros)

@app.route('/reciente', methods=['GET'])
def reciente():
    conn = sqlite3.connect('escuela.db')
    c = conn.cursor()

    # Obtiene las últimas 5 entradas de la tabla de comentarios
    c.execute("SELECT * FROM comentarios ORDER BY fecha DESC LIMIT 5")
    comentarios = c.fetchall()

    conn.close()

    return render_template('reciente.html', comentarios=comentarios)



if __name__ == '__main__':
    app.run(debug=True)
