# Script de linea de comandos (no se importa desde app.py) para poner al dia
# la tabla `usuarios` de una base de datos que ya existia ANTES de que
# Modulos/Usuarios.py tuviera las columnas password_hash y estado_aprobacion.
# Usa sqlite3 directo (no SQLAlchemy) para no depender del ORM al alterar
# el esquema. Se puede correr varias veces sin problema: si una columna ya
# existe, se omite.
#
# Uso: python migrar_usuarios.py
import sqlite3

from base_de_datos import URL_BASE_DATOS

RUTA_BASE_DATOS = URL_BASE_DATOS.replace("sqlite:///", "")


def columnas_actuales(cursor, tabla):
    cursor.execute(f"PRAGMA table_info({tabla})")
    return {fila[1] for fila in cursor.fetchall()}


def main():
    conexion = sqlite3.connect(RUTA_BASE_DATOS)
    try:
        cursor = conexion.cursor()
        columnas = columnas_actuales(cursor, "usuarios")

        if "password_hash" not in columnas:
            cursor.execute("ALTER TABLE usuarios ADD COLUMN password_hash TEXT")
            print("Columna 'password_hash' agregada.")
        else:
            print("Columna 'password_hash' ya existia, no se toca.")

        if "estado_aprobacion" not in columnas:
            # El DEFAULT se aplica tambien a las filas existentes (no solo a las nuevas),
            # asi los usuarios que ya estaban activos quedan aprobados y no se bloquean.
            cursor.execute(
                "ALTER TABLE usuarios ADD COLUMN estado_aprobacion TEXT DEFAULT 'APROBADO'"
            )
            print("Columna 'estado_aprobacion' agregada (usuarios existentes quedan en 'APROBADO').")
        else:
            print("Columna 'estado_aprobacion' ya existia, no se toca.")

        conexion.commit()
    finally:
        conexion.close()

    print("Migracion completada.")


if __name__ == "__main__":
    main()
