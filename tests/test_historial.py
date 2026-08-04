CLIENTE_VALIDO = {
    "nombre": "Cliente historial",
    "cliente_id": "CLI-HIST-001",
    "tipo_cliente": "empresa_privada",
    "estado_cliente": "activo",
    "condicion_pago": "30 dias",
    "estado_cartera_cliente": "al dia",
}


def _login(client, usuario_aprobado):
    respuesta = client.post(
        "/auth/login",
        json={
            "email": usuario_aprobado["email"],
            "contrasena": usuario_aprobado["password"],
        },
    )
    assert respuesta.status_code == 200


def test_historial_registra_creacion_y_actualizacion(client, usuario_aprobado):
    _login(client, usuario_aprobado)

    creado = client.post("/api/clientes", json=CLIENTE_VALIDO).json()["registro"]
    cliente_id = creado["id"]

    datos_actualizados = dict(CLIENTE_VALIDO)
    datos_actualizados["nombre"] = "Cliente historial renombrado"

    respuesta_put = client.put(f"/api/clientes/{cliente_id}", json=datos_actualizados)
    assert respuesta_put.status_code == 200

    respuesta_historial = client.get(f"/api/historial/clientes/{cliente_id}")
    assert respuesta_historial.status_code == 200
    entradas = respuesta_historial.json()["historial"]

    entrada_creacion = next((e for e in entradas if e["accion"] == "crear"), None)
    assert entrada_creacion is not None

    entrada_actualizacion = next(
        (e for e in entradas if e["accion"] == "actualizar" and e["campo"] == "nombre"),
        None,
    )
    assert entrada_actualizacion is not None
    assert entrada_actualizacion["valor_anterior"] == CLIENTE_VALIDO["nombre"]
    assert entrada_actualizacion["valor_nuevo"] == datos_actualizados["nombre"]
