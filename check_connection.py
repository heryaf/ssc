import sqlite3

def check_connection(db_name):
    try:
        conn = sqlite3.connect(db_name)
        print("Conexión exitosa a la base de datos")
    except sqlite3.Error as e:
        print(f"Ocurrió un error al conectar a la base de datos: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    check_connection('escuela.db')
