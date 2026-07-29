import getpass

from passlib.context import CryptContext

from Modulos.enums import RolUsuario, EstadoAprobacion
from Persistencia.UsuariosRepositorio import UsuariosRepositorio

contexto_password = CryptContext(schemes=["bcrypt"], deprecated="auto")


def main():
    usuarios = UsuariosRepositorio.obtener_todos()
    if any(u.rol == RolUsuario.ADMINISTRADOR_GENERAL for u in usuarios):
        print("Ya existe un usuario con rol Administrador general. No se crea ninguno.")
        return

    email = input("Correo del administrador: ").strip()
    password = getpass.getpass("Contraseña del administrador: ")

    password_hash = contexto_password.hash(password)

    UsuariosRepositorio.agregar(
        nombre_usuario=email,
        email=email,
        rol=RolUsuario.ADMINISTRADOR_GENERAL,
        estado="Activo",
        password_hash=password_hash,
        estado_aprobacion=EstadoAprobacion.APROBADO,
    )
    print(f"Administrador general creado: {email}")


if __name__ == "__main__":
    main()
