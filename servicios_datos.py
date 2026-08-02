# Capa generica que usa routers/datos.py para hacer CRUD sobre CUALQUIER tipo
# definido en catalogo_modelos.CATALOGO_DATOS, sin escribir un endpoint por
# entidad. Valida/convierte el payload segun la config de cada "campo" y
# delega en el repositorio del modelo si tiene metodos propios (obtener_todos,
# agregar, actualizar, eliminar), o en SQLAlchemy directo si no los tiene.
from datetime import datetime
from enum import Enum as PythonEnum

from fastapi import HTTPException

from base_de_datos import SesionLocal, logger
from Persistencia.HistorialRepositorio import HistorialRepositorio


def obtener_campos(configuracion):
    return configuracion.get("campos") or configuracion.get("fields") or []


def obtener_enumeraciones(configuracion):
    return configuracion.get("enumeraciones") or configuracion.get("enums") or {}


def obtener_modelo(configuracion):
    return configuracion.get("modelo") or configuracion.get("model")


def normalizar_payload(configuracion, datos):
    # Recorre SOLO los campos definidos en el catalogo para ese tipo (ignora
    # cualquier clave extra que venga en `datos`), valida obligatoriedad y
    # convierte tipos (enum/number/date) antes de pasarlos al repositorio.
    valores = {}
    enumeraciones = obtener_enumeraciones(configuracion)

    for configuracion_campo in obtener_campos(configuracion):
        nombre_campo = configuracion_campo["nombre"]
        valor = datos.get(nombre_campo)

        if valor in (None, ""):
            if not configuracion_campo.get("requerido", True):
                continue  # no se incluye la clave: deja que el default del repositorio aplique
            raise HTTPException(status_code=400, detail=f"Falta el campo '{nombre_campo}'")

        tipo_enum = enumeraciones.get(nombre_campo)
        if tipo_enum:
            try:
                valor = tipo_enum(valor)  # castea el string recibido al Enum correspondiente
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

        if configuracion_campo.get("tipo") == "boolean":
            valor_normalizado = str(valor).strip().lower()
            if valor_normalizado in ("si", "sí", "true", "1"):
                valor = True
            elif valor_normalizado in ("no", "false", "0"):
                valor = False
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"El campo '{nombre_campo}' debe ser 'Si' o 'No'",
                )

        if configuracion_campo.get("tipo") == "date":
            try:
                valor = datetime.strptime(valor, "%Y-%m-%d")
            except (TypeError, ValueError) as exc:
                raise HTTPException(
                    status_code=400,
                    detail=f"El campo '{nombre_campo}' debe tener formato de fecha YYYY-MM-DD",
                ) from exc

        valores[nombre_campo] = valor

    return valores


def serializar(registro, campos):
    # Convierte un registro (ORM u objeto de repositorio propio) a dict JSON-friendly,
    # traduciendo valores Enum a su .value.
    datos = {"id": registro.id}

    for configuracion_campo in campos:
        nombre_campo = configuracion_campo["nombre"]
        valor = getattr(registro, nombre_campo)
        datos[nombre_campo] = valor.value if isinstance(valor, PythonEnum) else valor

    return datos


# Las funciones CRUD de aqui abajo primero intentan usar los metodos propios
# del repositorio (obtener_todos/agregar/actualizar/eliminar); si el modelo no
# los define, caen a un CRUD generico via SQLAlchemy. Asi conviven modelos con
# repositorio a medida y modelos ORM simples bajo la misma capa.

def listar_registros(modelo):
    if hasattr(modelo, "obtener_todos"):
        return modelo.obtener_todos()
    with SesionLocal() as sesion:
        return sesion.query(modelo).all()


def _valor_historial(valor):
    # Los campos String de Historial no aceptan Enum ni datetime directamente.
    if valor is None:
        return None
    if isinstance(valor, PythonEnum):
        valor = valor.value
    return str(valor)


def _registrar_cambios_historial(tipo_entidad, entidad_id, registro_anterior, valores_nuevos, usuario_id, sesion=None):
    if not registro_anterior:
        return
    for nombre_campo, valor_nuevo in valores_nuevos.items():
        valor_anterior = getattr(registro_anterior, nombre_campo, None)
        if valor_anterior == valor_nuevo:
            continue
        HistorialRepositorio.registrar(
            tipo_entidad=tipo_entidad,
            entidad_id=entidad_id,
            accion="actualizar",
            usuario_id=usuario_id,
            campo=nombre_campo,
            valor_anterior=_valor_historial(valor_anterior),
            valor_nuevo=_valor_historial(valor_nuevo),
            sesion=sesion,
        )


def crear_registro(modelo, valores, usuario_id=None, tipo_entidad=None):
    # Una sola sesion/transaccion para el registro y su entrada de historial:
    # si cualquiera de las dos falla, ninguna queda guardada (ver except).
    sesion = SesionLocal()
    # Sin esto, tras el commit() de mas abajo el ORM "expira" los atributos
    # del objeto devuelto; como la sesion se cierra en el finally, cualquier
    # lectura posterior (p. ej. serializar() en routers/datos.py) reventaria
    # con DetachedInstanceError.
    sesion.expire_on_commit = False
    try:
        if hasattr(modelo, "agregar"):
            registro = modelo.agregar(**valores, sesion=sesion)
        else:
            registro = modelo(**valores)
            sesion.add(registro)
            sesion.flush()  # asigna el id antes de usarlo en el historial

        HistorialRepositorio.registrar(
            tipo_entidad=tipo_entidad,
            entidad_id=registro.id,
            accion="crear",
            usuario_id=usuario_id,
            sesion=sesion,
        )

        sesion.commit()
        return registro
    except Exception as exc:
        sesion.rollback()
        logger.error(
            "Fallo al crear registro tipo_entidad=%s usuario_id=%s: %s",
            tipo_entidad, usuario_id, exc,
        )
        raise
    finally:
        sesion.close()


def buscar_registro(modelo, registro_id):
    with SesionLocal() as sesion:
        return sesion.get(modelo, registro_id)


def actualizar_registro(modelo, registro_id, valores, usuario_id=None, tipo_entidad=None):
    sesion = SesionLocal()
    sesion.expire_on_commit = False
    try:
        if hasattr(modelo, "actualizar"):
            obtener_por_id = getattr(modelo, "obtener_por_id", None)
            registro_anterior = obtener_por_id(registro_id) if obtener_por_id else None
            _registrar_cambios_historial(tipo_entidad, registro_id, registro_anterior, valores, usuario_id, sesion=sesion)
            registro = modelo.actualizar(registro_id, sesion=sesion, **valores)
        else:
            registro = sesion.get(modelo, registro_id)
            if registro:
                _registrar_cambios_historial(tipo_entidad, registro_id, registro, valores, usuario_id, sesion=sesion)
                for nombre_campo, valor in valores.items():
                    setattr(registro, nombre_campo, valor)

        sesion.commit()
        return registro
    except Exception as exc:
        sesion.rollback()
        logger.error(
            "Fallo al actualizar registro tipo_entidad=%s registro_id=%s usuario_id=%s: %s",
            tipo_entidad, registro_id, usuario_id, exc,
        )
        raise
    finally:
        sesion.close()


def eliminar_registro(modelo, registro_id, usuario_id=None, tipo_entidad=None):
    sesion = SesionLocal()
    try:
        if hasattr(modelo, "eliminar"):
            # Se verifica existencia ANTES de eliminar porque el metodo propio
            # `eliminar` no siempre informa si realmente borro algo.
            obtener_por_id = getattr(modelo, "obtener_por_id", None)
            existe = obtener_por_id(registro_id) is not None if obtener_por_id else True
            if existe:
                HistorialRepositorio.registrar(
                    tipo_entidad=tipo_entidad,
                    entidad_id=registro_id,
                    accion="eliminar",
                    usuario_id=usuario_id,
                    sesion=sesion,
                )
                modelo.eliminar(registro_id, sesion=sesion)
        else:
            registro = sesion.get(modelo, registro_id)
            existe = registro is not None
            if existe:
                HistorialRepositorio.registrar(
                    tipo_entidad=tipo_entidad,
                    entidad_id=registro_id,
                    accion="eliminar",
                    usuario_id=usuario_id,
                    sesion=sesion,
                )
                sesion.delete(registro)

        sesion.commit()
        return existe
    except Exception as exc:
        sesion.rollback()
        logger.error(
            "Fallo al eliminar registro tipo_entidad=%s registro_id=%s usuario_id=%s: %s",
            tipo_entidad, registro_id, usuario_id, exc,
        )
        raise
    finally:
        sesion.close()
