ROL_DE_PRUEBA = "Ejecutivo comercial"


def test_registro_valido_devuelve_pendiente_de_aprobacion(client):
    respuesta = client.post(
        "/auth/registro",
        json={
            "email": "nuevo.usuario@test.com",
            "contrasena": "Clave123!",
            "rol": ROL_DE_PRUEBA,
        },
    )

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["success"] is True
    assert "pendiente de aprobación" in cuerpo["message"]


def test_registro_email_duplicado_devuelve_400(client):
    datos = {
        "email": "duplicado@test.com",
        "contrasena": "Clave123!",
        "rol": ROL_DE_PRUEBA,
    }

    primera_respuesta = client.post("/auth/registro", json=datos)
    assert primera_respuesta.status_code == 200

    segunda_respuesta = client.post("/auth/registro", json=datos)
    assert segunda_respuesta.status_code == 400


def test_registro_contrasena_debil_devuelve_422(client):
    respuesta = client.post(
        "/auth/registro",
        json={
            "email": "contrasena.debil@test.com",
            # Sin mayuscula: no cumple validar_complejidad_contrasena en routers/auth.py.
            "contrasena": "clave123!",
            "rol": ROL_DE_PRUEBA,
        },
    )

    assert respuesta.status_code == 422


def test_login_usuario_pendiente_devuelve_403(client):
    datos = {
        "email": "pendiente.aprobacion@test.com",
        "contrasena": "Clave123!",
        "rol": ROL_DE_PRUEBA,
    }
    registro = client.post("/auth/registro", json=datos)
    assert registro.status_code == 200

    respuesta = client.post(
        "/auth/login",
        json={"email": datos["email"], "contrasena": datos["contrasena"]},
    )

    assert respuesta.status_code == 403


def test_login_usuario_aprobado_devuelve_200_y_cookie_sesion(client, usuario_aprobado):
    respuesta = client.post(
        "/auth/login",
        json={
            "email": usuario_aprobado["email"],
            "contrasena": usuario_aprobado["password"],
        },
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["success"] is True
    assert "session" in respuesta.cookies


def test_login_contrasena_incorrecta_devuelve_401(client, usuario_aprobado):
    respuesta = client.post(
        "/auth/login",
        json={
            "email": usuario_aprobado["email"],
            "contrasena": "ClaveIncorrecta123!",
        },
    )

    assert respuesta.status_code == 401
