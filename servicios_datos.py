from enum import Enum as PythonEnum

from fastapi import HTTPException

from base_de_datos import SesionLocal


def obtener_campos(configuracion):
    return configuracion.get("campos") or configuracion.get("fields") or []


def obtener_enumeraciones(configuracion):
    return configuracion.get("enumeraciones") or configuracion.get("enums") or {}


def obtener_modelo(configuracion):
    return configuracion.get("modelo") or configuracion.get("model")


def normalizar_payload(configuracion, datos):
    valores = {}
    enumeraciones = obtener_enumeraciones(configuracion)

    for configuracion_campo in obtener_campos(configuracion):
        nombre_campo = configuracion_campo["nombre"]
        valor = datos.get(nombre_campo)

        if valor in (None, ""):
            if not configuracion_campo.get("requerido", True):
                valores[nombre_campo] = None
                continue
            raise HTTPException(status_code=400, detail=f"Falta el campo '{nombre_campo}'")

        tipo_enum = enumeraciones.get(nombre_campo)
        if tipo_enum:
            try:
                valor = tipo_enum(valor)
            except ValueError as exc:
                opciones = ", ".join(item.value for item in tipo_enum)
                raise HTTPException(
                    status_code=400,
                    detail=f"Valor invalido para '{nombre_campo}'. Usa: {opciones}",
                ) from exc

        if configuracion_campo.get("tipo") == "number":
            try:
                valor = float(valor)
            except (TypeError, ValueError) as exc:
                raise HTTPException(
                    status_code=400,
                    detail=f"El campo '{nombre_campo}' debe ser numerico",
                ) from exc

        valores[nombre_campo] = valor

    return valores


def serializar(registro, campos):
    datos = {"id": registro.id}

    for configuracion_campo in campos:
        nombre_campo = configuracion_campo["nombre"]
        valor = getattr(registro, nombre_campo)
        datos[nombre_campo] = valor.value if isinstance(valor, PythonEnum) else valor

    return datos


def listar_registros(modelo):
    with SesionLocal() as sesion:
        return sesion.query(modelo).all()


def crear_registro(modelo, valores):
    with SesionLocal() as sesion:
        registro = modelo(**valores)
        sesion.add(registro)
        sesion.commit()
        sesion.refresh(registro)
        return registro


def buscar_registro(modelo, registro_id):
    with SesionLocal() as sesion:
        return sesion.get(modelo, registro_id)


def actualizar_registro(modelo, registro_id, valores):
    with SesionLocal() as sesion:
        registro = sesion.get(modelo, registro_id)

        if not registro:
            return None

        for nombre_campo, valor in valores.items():
            setattr(registro, nombre_campo, valor)

        sesion.commit()
        sesion.refresh(registro)
        return registro


def eliminar_registro(modelo, registro_id):
    with SesionLocal() as sesion:
        registro = sesion.get(modelo, registro_id)

        if not registro:
            return False

        sesion.delete(registro)
        sesion.commit()
        return True
