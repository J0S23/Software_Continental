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
- `modelos`
- `equipos`
- `insumos`
- `polizas`
- `repuestos`
- `mano_obra`
- `impuestos`
- `valor_facturado`

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

## Organizacion

`app.py` queda como punto de entrada. La configuracion de tablas y campos vive en `catalogo_modelos.py`, las operaciones de base de datos en `servicios_datos.py`, las rutas de pagina en `routers/paginas.py`, y la conexion a SQLite en `base_de_datos.py`.

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
|-- templates/
|   `-- index.html
|-- static/
|   |-- style.css
|   `-- script.js
`-- Variables/
    |-- Clientes.py
    |-- Modelos.py
    |-- Insumos.py
    |-- Poliza.py
    |-- Repuestos.py
    |-- Costos.py
    |-- Facturacion.py
    `-- enums.py
```

## Compatibilidad

`database.py` y `model_registry.py` se mantienen como alias para codigo anterior, pero el codigo nuevo debe importar desde los modulos con nombres en espanol.
