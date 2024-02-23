from flask import Flask, render_template, request  # Importa las clases necesarias desde Flask

app = Flask(__name__)  # Inicializa la aplicación Flask

def max_execution_plus_wait(process_info):
    # Función que calcula la suma del tiempo de ejecución y espera máximos entre los procesos
    max_exec_plus_wait = 0  # Inicializa la variable que almacenará el valor máximo de tiempo ejecución + espera
    for _, _, tiempo_ejecucion, tiempo_espera, _ in process_info:
        exec_plus_wait = tiempo_ejecucion + tiempo_espera  # Calcula el tiempo de ejecución + espera para un proceso
        if exec_plus_wait > max_exec_plus_wait:  # Compara con el valor máximo actual
            max_exec_plus_wait = exec_plus_wait  # Actualiza el valor máximo si es necesario
    return max_exec_plus_wait  # Devuelve el tiempo máximo de ejecución + espera

def sjn_scheduler(procesos):
    # Función que implementa el algoritmo de planificación de procesos "Shortest Job Next" (SJN)
    tiempo_actual = 0  # Tiempo actual del sistema
    tiempo_espera_total = 0  # Tiempo total de espera de los procesos
    tiempo_servicio_total = 0  # Tiempo total de servicio de los procesos
    procesos_terminados = []  # Lista de procesos terminados
    secuencia = []  # Secuencia de ejecución de procesos
    informacion_proceso = []  # Información detallada de los procesos+

    tiempo_espera_maximo = 0  # Tiempo de espera máximo entre los procesos

    while procesos:  # Mientras haya procesos en la lista
        procesos_elegibles = [p for p in procesos if p[1] <= tiempo_actual]  # Procesos elegibles en el momento actual

        if not procesos_elegibles:  # Si no hay procesos elegibles en el momento actual
            tiempo_actual += 1  # Incrementa el tiempo actual y continúa con el bucle
            continue

        proceso_mas_corto = min(procesos_elegibles, key=lambda x: x[2])  # Proceso con el tiempo de ejecución más corto

        id_proceso, tiempo_llegada, tiempo_ejecucion = proceso_mas_corto  # Detalles del proceso seleccionado

        tiempo_espera = tiempo_actual - tiempo_llegada  # Calcula el tiempo de espera para el proceso
        tiempo_espera_total += tiempo_espera  # Actualiza el tiempo total de espera

        informacion_proceso.append((id_proceso, tiempo_llegada, tiempo_ejecucion, tiempo_espera, tiempo_actual + tiempo_ejecucion))  # Agrega información del proceso

        tiempo_espera_maximo = max(tiempo_espera_maximo, tiempo_espera)  # Actualiza el tiempo de espera máximo

        tiempo_actual += tiempo_ejecucion  # Incrementa el tiempo actual considerando el tiempo de ejecución del proceso

        procesos.remove(proceso_mas_corto)  # Remueve el proceso de la lista de procesos
        procesos_terminados.append(id_proceso)  # Agrega el proceso a la lista de procesos terminados
        secuencia.append(id_proceso)  # Agrega el proceso a la secuencia de ejecución

    if len(procesos_terminados) > 0:  # Si hay procesos terminados
        tiempo_espera_promedio = tiempo_espera_total / len(procesos_terminados)  # Calcula el tiempo de espera promedio

        informacion_proceso.sort(key=lambda x: x[0])  # Ordena la información de los procesos por ID

        tiempo_en_sistema = {}  # Tiempo que cada proceso pasa en el sistema
        tiempo_ejecucion_total = {}  # Tiempo total de ejecución de cada proceso

        for id_proceso, tiempo_llegada, tiempo_ejecucion, tiempo_espera, tiempo_final in informacion_proceso:
            tiempo_en_sistema[id_proceso] = tiempo_final - tiempo_llegada  # Calcula el tiempo en el sistema para cada proceso
            tiempo_ejecucion_total[id_proceso] = tiempo_ejecucion  # Almacena el tiempo de ejecución total de cada proceso

            tiempo_servicio = tiempo_ejecucion - tiempo_espera  # Calcula el tiempo de servicio de cada proceso
            tiempo_servicio_total += tiempo_servicio  # Actualiza el tiempo total de servicio

        tiempo_ejecucion_mas_espera = max_execution_plus_wait(informacion_proceso)  # Calcula el tiempo máximo de ejecución + espera

        # Almacena los resultados de la planificación SJN en un diccionario
        results = {
            'tiempo_espera_promedio': tiempo_espera_promedio,
            'secuencia': ' -> '.join(secuencia),
            'informacion_proceso': informacion_proceso,
            'tiempo_en_sistema': tiempo_en_sistema,
            'tiempo_ejecucion_total': tiempo_ejecucion_total,
        }
        return results  # Devuelve los resultados de la planificación SJN
    else:
        return None  # Devuelve None si no se ingresaron procesos válidos

@app.route('/', methods=['GET', 'POST'])  # Ruta para la página principal, acepta métodos GET y POST
def index():
    if request.method == 'POST':  # Si se envía una solicitud POST desde el formulario
        num_procesos = int(request.form['num_procesos'])  # Obtiene el número de procesos del formulario
        procesos = []

        for i in range(num_procesos):
            id_proceso = chr(65 + i)  # Genera IDs para los procesos (A, B, C, ...)
            tiempo_llegada = int(request.form[f"tiempo_llegada_{i}"])  # Obtiene el tiempo de llegada del formulario
            tiempo_ejecucion = int(request.form[f"tiempo_ejecucion_{i}"])  # Obtiene el tiempo de ejecución del formulario
            procesos.append((id_proceso, tiempo_llegada, tiempo_ejecucion))  # Agrega información del proceso a la lista

        results = sjn_scheduler(procesos)  # Aplica el algoritmo SJN a los procesos ingresados
        if results:  # Si hay resultados de la planificación SJN
            return render_template('results.html', results=results)  # Muestra los resultados en la plantilla results.html
        else:
            return "No se ingresaron procesos válidos."  # Muestra un mensaje si no se ingresaron procesos válidos
    return render_template('index.html')  # Renderiza el formulario inicial si no se ha enviado una solicitud POST

if __name__ == "__main__":
    app.run(debug=True)  # Ejecuta la aplicación Flask en modo debug
