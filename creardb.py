import sqlite3

# Conectarse a la base de datos
conn = sqlite3.connect('escuela.db')
c = conn.cursor()

# Crear tabla datos_alumno
c.execute('''
    CREATE TABLE datos_alumno (
        matricula TEXT PRIMARY KEY,
        grupo TEXT,
        nombre TEXT,
        apepat TEXT,
        apemat TEXT
    )
''')

# Crear tabla comentarios
c.execute('''
    CREATE TABLE comentarios (
        matricula TEXT,
        fecha DATE,
        comentario TEXT,
        FOREIGN KEY(matricula) REFERENCES datos_alumno(matricula)
    )
''')

# Crear tabla usuarios
c.execute('''
    CREATE TABLE usuarios (
        usuario TEXT,
        password TEXT
    )
''')

# Guardar los cambios y cerrar la conexión a la base de datos
conn.commit()
conn.close()
