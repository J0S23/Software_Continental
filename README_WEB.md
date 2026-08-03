# Gestor de Datos Continental

Aplicacion web local construida con FastAPI, SQLite y JavaScript vanilla para registrar datos operacionales de Continental.

## Requisitos

- Python 3.8+
- Dependencias de `requirements.txt`

## Instalacion

```bash
pip install -r requirements.txt
```

## Ejecutar

```bash
python app.py
```

Abre en el navegador:

```text
http://127.0.0.1:5000/
```

FastAPI no abre el navegador automaticamente; el servidor queda activo en la terminal.

## Tipos disponibles

- `clientes`
- `equipos`
- `insumos`
- `contratos`
- `repuestos`
- `servicios`
- `costos`
- `facturacion`
- `usuarios`

## API

| Metodo | Ruta | Descripcion |
| --- | --- | --- |
| `GET` | `/` | Interfaz web |
| `GET` | `/api/tipos` | Lista de tipos disponibles |
| `GET` | `/api/configuracion` | Campos usados por el frontend |
| `GET` | `/api/{tipo}` | Lista registros del tipo indicado |
| `POST` | `/api/{tipo}` | Crea un registro |
| `PUT` | `/api/{tipo}/{id}` | Edita un registro |
| `DELETE` | `/api/{tipo}/{id}` | Elimina un registro |

Ejemplo para crear un cliente:

```json
{
  "tipo_cliente": "Empresa",
  "estado_cliente": "Activo",
  "tipo_contacto": "Email",
  "condicion_pago": "Credito",
  "estado_cartera_cliente": "Al dia"
}
```

Para editar un cliente, envia los mismos campos con `PUT`:

```text
PUT /api/clientes/1
```

## Base de datos

La aplicacion usa SQLite en `continental_app.db`. Ese archivo contiene datos reales de la app, asi que no se debe borrar como parte de una limpieza normal.

## Migraciones

Los cambios de esquema (agregar/quitar columnas o tablas) van por Alembic, no a mano:

```bash
alembic revision --autogenerate -m "descripcion del cambio"
```

Revisa siempre el archivo generado en `alembic/versions/` antes de aplicarlo. Autogenerate compara los modelos contra la base real completa, asi que si hay diferencias previas sin migrar (drift) las va a incluir tambien -- no solo el cambio que queres hacer. Si el archivo trae de mas, edita `upgrade()`/`downgrade()` a mano para dejar solo lo que corresponde a este cambio, y deja el resto del drift para una migracion aparte y deliberada. Cuando el archivo refleja solo lo que queres:

```bash
alembic upgrade head
```

`crear_tablas()` (en `base_de_datos.py`, llamada desde `app.py` al arrancar) sigue existiendo, pero queda solo para levantar una base nueva y vacia en desarrollo o pruebas: crea las tablas que falten y nunca modifica una tabla que ya existe. No sirve para aplicar cambios de esquema a una base con datos -- eso es trabajo de Alembic.

## Organizacion

`app.py` queda como punto de entrada: monta los routers, importa los modelos que no tienen CRUD generico (para que `crear_tablas()` los registre) y arranca uvicorn. La configuracion de tablas y campos vive en `catalogo_modelos.py`, las operaciones de base de datos en `servicios_datos.py`, las rutas de pagina en `routers/paginas.py`, las rutas de datos en `routers/datos.py`, y la conexion a SQLite en `base_de_datos.py`. Los modelos SQLAlchemy de cada entidad viven en `Modulos/`.

```text
Continental.py/
|-- app.py
|-- base_de_datos.py
|-- catalogo_modelos.py
|-- configuracion.py
|-- servicios_datos.py
|-- requirements.txt
|-- continental_app.db
|-- routers/
|   |-- datos.py
|   `-- paginas.py
|-- Modulos/
|   |-- Cartera.py
|   |-- Clientes.py
|   |-- Contratos.py
|   |-- Costos.py
|   |-- Dashboard.py
|   |-- enums.py
|   |-- Equipos.py
|   |-- Facturacion.py
|   |-- Informes_mensuales.py
|   |-- Insumos.py
|   |-- Lecturas.py
|   |-- Rentabilidad.py
|   |-- Repuestos.py
|   |-- Sedes.py
|   |-- Servicio.py
|   `-- Usuarios.py
|-- templates/
|   `-- index.html
`-- static/
    |-- style.css
    `-- script.js
```
