
#Sin tabla propia, igual que Informes_mensuales y Dashboard: lee los
#modelos existentes y devuelve alertas calculadas en el momento.

#Bloqueadas por falta de datos en el modelo actual (no se inventan):
#- Stock bajo de consumibles: Insumos no tiene columna de stock.
# Tonerentregados con frecuencia inusual: no hay registro transaccional
#de entregas (mismo motivo que en Informes_mensuales).
#Equipos con fallas recurrentes / mantenimientos: Servicio (correctivo)
# #no tiene un contador de fallas por equipo todavia