from datetime import time, date, datetime
import calendar
import pandas as pd
import math # Import the math module

vacaciones_empleados = {
    "Andres Cortez": [[datetime(2026, 3, 1).date(), datetime(2026, 3, 14).date()]],
    "Andres Polanco": [],
    "Camilo Castillo": [],
    "Carlos Olaya": [[datetime(2026, 2, 2).date(), datetime(2026, 2, 8).date()]],
    "Eduardo Sanchez": [],
    "Felipe Claros": [],
    "Heinert Zuniga": [[datetime(2026, 4, 4).date(), datetime(2026, 4, 11).date()]],
    "Jhon Fredy Mapallo": [],
    "Karen Mapallo": [],
    "Maria Lopez": [],
    "Nicolas Bravo": [],
    "Steven Rodriguez": [[datetime(2026, 2, 9).date(), datetime(2026, 2, 27).date()]]
}
dias_festivos_especiales = {
    datetime(2026, 3, 23).date(): "medio_dia"
}

def eliminar_duplicados_cercanos(registros, tolerancia_minutos=5):

    registros_filtrados = [registros[0]]

    for actual in registros[1:]:
        diferencia = (actual - registros_filtrados[-1]).total_seconds() / 60

        if diferencia > tolerancia_minutos:
            registros_filtrados.append(actual)

    return registros_filtrados

def horas_a_reloj(horas_decimal):

    if pd.isna(horas_decimal):
        return "-"

    total_minutos = int(round(horas_decimal * 60))

    horas = total_minutos // 60
    minutos = total_minutos % 60

    return f"{horas}h {minutos:02d}m"

def calcular_horas_esperadas(año, mes, vacaciones_del_empleado, dias_festivos_especiales):
    total_dias = calendar.monthrange(año, mes)[1]
    horas_esperadas = 0

    for dia_num in range(1, total_dias + 1):
        current_date = date(año, mes, dia_num)

        # Check for vacation days
        es_vacacion = False
        for rango_vacacion in vacaciones_del_empleado:
            start_date, end_date = rango_vacacion
            if start_date <= current_date <= end_date:
                es_vacacion = True
                break
        if es_vacacion:
            continue # Skip vacation days for expected hours calculation

        # Check for special holidays
        if current_date in dias_festivos_especiales:
            if dias_festivos_especiales[current_date] == "medio_dia":
                horas_esperadas += 5.5 # 5 hours 30 minutes (7:35 to 13:05)
        else: # Monday to Saturday
            horas_esperadas += 9 # 9 hours (7:35-11:30 and 13:00-18:05)
    return horas_esperadas

def crear_df(path):
    path = '/content/Informe de los registros originales.csv'
    df = pd.read_csv(path, encoding='latin1')
    columns_to_drop = [
        'Departamento',
        'Estado de asistencia',
        'Punto de verificación de asistencia',
        'Nombre personalizado',
        'Fuente de datos',
        'Gestión de informe',
        'Temperatura',
        'Anormal'
    ]
    df = df.drop(columns=columns_to_drop, errors='ignore')

    df['ID de persona'] = df['ID de persona'].str.replace("'", '', regex=False)
    df = df.rename(columns={'ID de persona': 'ID'})

    df['Hora'] = pd.to_datetime(df['Hora'])
    df['Fecha'] = df['Hora'].dt.date
    df = df.sort_values(['Nombre', 'Hora'])
    return df

HORA_LIMITE_ENTRADA = time(7, 35)
HORA_SALIDA_OFICIAL = time(18, 0)

def promedio_hora(serie_horas):
    # eliminar valores nulos
    serie_horas = serie_horas.dropna()

    if len(serie_horas) == 0:
        return "-"

    minutos = [
        h.hour * 60 + h.minute + h.second / 60
        for h in serie_horas
    ]

    promedio_min = sum(minutos) / len(minutos)

    horas = int(promedio_min // 60)
    mins = int(promedio_min % 60)

    return f"{horas:02d}:{mins:02d}"

def procesar_dia(grupo):
    grupo = grupo.sort_values('Hora')
    registros = grupo['Hora'].tolist()
    registros = eliminar_duplicados_cercanos(registros)
    fecha = grupo['Fecha'].iloc[0]

    es_dia_festivo_especial = fecha in dias_festivos_especiales
    tipo_dia_festivo = dias_festivos_especiales.get(fecha)

    es_domingo = fecha.weekday() == 6

    resultado = {
        "Detalle_Marcaciones": "",
        "Entrada": None,
        "Salida_Almuerzo": None,
        "Entrada_Almuerzo": None,
        "Salida_Final": None,
        "Horas_Trabajadas": 0,
        "Tardanza": 0,
        "Tiempo_extra": 0,
        "Minutos_Tarde": 0,
        "Inconsistencia": None
    }
    if es_domingo:
      if len(registros) == 2:
        entrada = registros[0]
        salida_final = registros[1]

        resultado["Entrada"] = entrada
        resultado["Salida_Final"] = salida_final

        horas = salida_final - entrada
        resultado["Horas_Trabajadas"] = horas.total_seconds() / 3600

        # Tardanza domingo
        if entrada.time() > time(8, 10):
            resultado["Tardanza"] = 1
            minutos = (
                datetime.combine(fecha, entrada.time()) -
                datetime.combine(fecha, time(8, 10))
            ).total_seconds() / 60

            resultado["Minutos_Tarde"] = math.ceil(minutos) # Use math.ceil
            resultado["Inconsistencia"] = "Entrada tardia"
            resultado["Detalle_Marcaciones"] = entrada.strftime("%H:%M")
        # Salida anticipada domingo
        if salida_final.time() < time(13, 0):
          resultado["Inconsistencia"] = "Salida anticipada"
          resultado["Detalle_Marcaciones"] = salida_final.strftime("%H:%M")
      elif len(registros) == 1:
        resultado["Inconsistencia"] = f"{len(registros)} marcacion"
        resultado["Detalle_Marcaciones"] = ", ".join(
            [r.strftime("%H:%M") for r in registros]
        )
    elif es_dia_festivo_especial and tipo_dia_festivo == "medio_dia": # Nuevo bloque de lógica
        if len(registros) == 2:
            entrada = registros[0]
            salida_final = registros[1]
            resultado["Entrada"] = entrada
            resultado["Salida_Final"] = salida_final
            horas = salida_final - entrada
            resultado["Horas_Trabajadas"] = horas.total_seconds() / 3600
        else:
            resultado["Inconsistencia"] = f"{len(registros)} marcaciones para medio día"
            resultado["Detalle_Marcaciones"] = ", ".join(
                [r.strftime("%H:%M") for r in registros]
            )
    else:
    # Lógica normal (lunes a sábado)
      if len(registros) == 4:
        entrada = registros[0]
        salida_alm = registros[1]
        entrada_alm = registros[2]
        salida_final = registros[3]

        resultado["Entrada"] = entrada
        resultado["Salida_Almuerzo"] = salida_alm
        resultado["Entrada_Almuerzo"] = entrada_alm
        resultado["Salida_Final"] = salida_final

        horas = (salida_alm - entrada) + (salida_final - entrada_alm)
        resultado["Horas_Trabajadas"] = horas.total_seconds() / 3600
        if salida_final.time() > time(18, 0):
          minutos = (
                datetime.combine(fecha, salida_final.time()) -
                datetime.combine(fecha, time(18, 0))
            ).total_seconds() / 60
          resultado["Tiempo_extra"] = math.ceil(minutos) # Use math.ceil

        if entrada.time() > time(7, 35):
            resultado["Tardanza"] = 1
            minutos = (
                datetime.combine(fecha, entrada.time()) -
                datetime.combine(fecha, time(7, 35))
            ).total_seconds() / 60
            resultado["Minutos_Tarde"] = math.ceil(minutos) # Use math.ceil

            resultado["Inconsistencia"] = "Entrada tardia"
            resultado["Detalle_Marcaciones"] = entrada.strftime("%H:%M")

        if salida_final.time() < time(18, 0):
            resultado["Inconsistencia"] = "Salida anticipada"
            resultado["Detalle_Marcaciones"] = salida_final.strftime("%H:%M")

      else:
        resultado["Inconsistencia"] = f"{len(registros)} marcaciones"
        resultado["Detalle_Marcaciones"] = ", ".join(
            [r.strftime("%H:%M") for r in registros]
        )

    return pd.Series(resultado)

resumen = df.groupby(['Nombre', 'Fecha', 'ID']).apply(procesar_dia).reset_index()
