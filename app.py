from flask import Flask, render_template, request

app = Flask(__name__)

def max_execution_plus_wait(process_info):
    max_exec_plus_wait = 0
    for _, _, tiempo_ejecucion, tiempo_espera, _ in process_info:
        exec_plus_wait = tiempo_ejecucion + tiempo_espera
        if exec_plus_wait > max_exec_plus_wait:
            max_exec_plus_wait = exec_plus_wait
    return max_exec_plus_wait

def sjn_scheduler(procesos):
    tiempo_actual = 0
    tiempo_espera_total = 0
    tiempo_servicio_total = 0
    procesos_terminados = []
    secuencia = []
    informacion_proceso = []

    tiempo_espera_maximo = 0

    while procesos:
        procesos_elegibles = [p for p in procesos if p[1] <= tiempo_actual]

        if not procesos_elegibles:
            tiempo_actual += 1
            continue

        proceso_mas_corto = min(procesos_elegibles, key=lambda x: x[2])

        id_proceso, tiempo_llegada, tiempo_ejecucion = proceso_mas_corto

        tiempo_espera = tiempo_actual - tiempo_llegada
        tiempo_espera_total += tiempo_espera

        informacion_proceso.append((id_proceso, tiempo_llegada, tiempo_ejecucion, tiempo_espera, tiempo_actual + tiempo_ejecucion))

        tiempo_espera_maximo = max(tiempo_espera_maximo, tiempo_espera)

        tiempo_actual += tiempo_ejecucion

        procesos.remove(proceso_mas_corto)
        procesos_terminados.append(id_proceso)
        secuencia.append(id_proceso)

    if len(procesos_terminados) > 0:
        tiempo_espera_promedio = tiempo_espera_total / len(procesos_terminados)

        informacion_proceso.sort(key=lambda x: x[0])

        tiempo_en_sistema = {}
        tiempo_ejecucion_total = {}

        for id_proceso, tiempo_llegada, tiempo_ejecucion, tiempo_espera, tiempo_final in informacion_proceso:
            tiempo_en_sistema[id_proceso] = tiempo_final - tiempo_llegada
            tiempo_ejecucion_total[id_proceso] = tiempo_ejecucion

            tiempo_servicio = tiempo_ejecucion - tiempo_espera
            tiempo_servicio_total += tiempo_servicio

        tiempo_ejecucion_mas_espera = max_execution_plus_wait(informacion_proceso)

        results = {
            'tiempo_espera_promedio': tiempo_espera_promedio,
            'secuencia': ' -> '.join(secuencia),
            'informacion_proceso': informacion_proceso,
            'tiempo_en_sistema': tiempo_en_sistema,
            'tiempo_ejecucion_total': tiempo_ejecucion_total,
        }
        return results
    else:
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        num_procesos = int(request.form['num_procesos'])
        procesos = []

        for i in range(num_procesos):
            id_proceso = chr(65 + i)
            tiempo_llegada = int(request.form[f"tiempo_llegada_{i}"])
            tiempo_ejecucion = int(request.form[f"tiempo_ejecucion_{i}"])
            procesos.append((id_proceso, tiempo_llegada, tiempo_ejecucion))

        results = sjn_scheduler(procesos)
        if results:
            return render_template('results.html', results=results)
        else:
            return "No se ingresaron procesos válidos."
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)
