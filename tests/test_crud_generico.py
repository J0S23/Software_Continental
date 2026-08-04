CLIENTE_VALIDO = {
    "nombre": "Cliente de prueba",
    "cliente_id": "CLI-001",
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


def test_get_clientes_sin_sesion_devuelve_401(client):
    respuesta = client.get("/api/clientes")

    assert respuesta.status_code == 401


def test_post_clientes_con_datos_validos_devuelve_200_y_registro_creado(client, usuario_aprobado):
    _login(client, usuario_aprobado)

    respuesta = client.post("/api/clientes", json=CLIENTE_VALIDO)

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["success"] is True
    assert cuerpo["registro"]["nombre"] == CLIENTE_VALIDO["nombre"]
    assert cuerpo["registro"]["cliente_id"] == CLIENTE_VALIDO["cliente_id"]
    assert "id" in cuerpo["registro"]


def test_get_clientes_despues_de_crear_incluye_el_registro(client, usuario_aprobado):
    _login(client, usuario_aprobado)

    creado = client.post("/api/clientes", json=CLIENTE_VALIDO).json()["registro"]

    respuesta = client.get("/api/clientes")

    assert respuesta.status_code == 200
    ids = [registro["id"] for registro in respuesta.json()["datos"]]
    assert creado["id"] in ids


def test_put_clientes_cambia_un_campo_y_lo_refleja_en_la_respuesta(client, usuario_aprobado):
    _login(client, usuario_aprobado)

    creado = client.post("/api/clientes", json=CLIENTE_VALIDO).json()["registro"]

    datos_actualizados = dict(CLIENTE_VALIDO)
    datos_actualizados["nombre"] = "Cliente renombrado"

    respuesta = client.put(f"/api/clientes/{creado['id']}", json=datos_actualizados)

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["success"] is True
    assert cuerpo["registro"]["nombre"] == "Cliente renombrado"


def test_delete_clientes_devuelve_200_y_el_registro_ya_no_aparece(client, usuario_aprobado):
    _login(client, usuario_aprobado)

    creado = client.post("/api/clientes", json=CLIENTE_VALIDO).json()["registro"]

    respuesta = client.delete(f"/api/clientes/{creado['id']}")

    assert respuesta.status_code == 200
    assert respuesta.json()["success"] is True

    ids_restantes = [registro["id"] for registro in client.get("/api/clientes").json()["datos"]]
    assert creado["id"] not in ids_restantes
