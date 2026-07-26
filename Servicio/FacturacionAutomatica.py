#Requiere un contrato con condiciones económicas configuradas y una lectura del período a facturar; de lo contrario, devuelve None

from Modulos import Lecturas
from Modulos.Informes_mensuales import _parse_periodo


def _lectura_actual_y_anterior(contrato_id, periodo):
    
    #Lectura del periodo pedido y la ultima lectura anterior a ese periodo, ambas del mismo contrato. 
    #Se usa contrato_id (no equipo_id) porque un contrato puede haber cambiado de equipo (CambiosRetiro) y
    #lo que importa para facturar es el historial del contrato.

    mes, anio = _parse_periodo(periodo)
    lecturas = Lecturas.obtener_por_contrato(contrato_id)

    lecturas_periodo = [l for l in lecturas if l.periodo == periodo]
    anteriores = [
        l for l in lecturas
        if l.fecha_lectura and (l.fecha_lectura.year, l.fecha_lectura.month) < (anio, mes)
    ]

    lectura_actual = lecturas_periodo[-1] if lecturas_periodo else None
    lectura_anterior = anteriores[-1] if anteriores else None
    return lectura_actual, lectura_anterior