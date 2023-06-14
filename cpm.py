
import networkx as nx
import matplotlib.pyplot as plt
import tkinter as tk
#Importar las librerías necesarias
from criticalpath import Node
import datetime
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import numpy as np


def funciones():
    guardar_datos()
    encontrar_ruta_critica()

# primer metodo
# crea calendario y diagrama de gantt
def guardar_datos():
    # proyecto nodos
    p = Node('proyecto')  
    global entrada_vars
    tareas=[]
    dependencias=[]
    for i in range(len(entrada_vars)):
        nodo = entrada_vars[i][0].get()
        duracion = entrada_vars[i][1].get()
        dependencia = entrada_vars[i][2].get()
        tareas.append( (nodo,{"duracion":duracion}) )

        p.add(Node(nodo, duration=int(duracion)))
        if dependencia!="":
            dependencia = dependencia.split(",")
            for j in range (len(dependencia)):
                p.link(dependencia[j],nodo)
                dependencias.append((dependencia[j],nodo))

    # Actualizar el proyecto:
    p.update_all()
    #Obtener la Ruta Crítica del modelo
    print("Ruta critica: ")
    print(p.get_critical_path())
    print("Duracion:")
    print(p.duration)

    ruta_critica = [str(n) for n in p.get_critical_path()]

    proj_fecha_inicio = datetime.date.today()

    # calendario 
    proj_calendario = pd.DataFrame([dict(Tarea = key, 
                                    Inicio = datetime.date.today(), 
                                    Fin = datetime.date.today() + datetime.timedelta(int(val['duracion'])), 
                                    Status = 'Actividad Normal')
                                for key, val in dict(tareas).items()])

    for key, val in dict(tareas).items():
        dep = [d for d in dependencias if d[1] == key]
        prev_tareas = [t[0] for t in dep]
        if prev_tareas:
            prev_fin = proj_calendario[proj_calendario.Tarea.isin(prev_tareas)]['Fin'].max()
            proj_calendario.loc[proj_calendario.Tarea == key, 'Inicio'] = prev_fin
            proj_calendario.loc[proj_calendario.Tarea == key, 'Fin'] = prev_fin + datetime.timedelta(int(val['duracion']))
            
    proj_calendario.loc[proj_calendario.Tarea.isin(ruta_critica), 'Status'] = 'Ruta Crítica'
    
    # en que dia inicia (si es la primer tarea en el dia cero)
    proj_calendario['dias_inicio'] = (proj_calendario.Inicio-proj_fecha_inicio).dt.days
    # Número de días desde que el proyecto inicia hasta que la tarea finaliza (acumulado)
    proj_calendario['dias_fin'] = (proj_calendario.Fin-proj_fecha_inicio).dt.days
    # Días entre el inicio y el fin de cada tarea
    proj_calendario['dias_inicio_fin'] = proj_calendario.dias_fin - proj_calendario.dias_inicio

    print("\nCalendario")
    print(proj_calendario)
    encontrar_ruta_critica()


    #Graficar las actividades en un diagrama de Gantt
    fig, ax = plt.subplots(1, figsize=(10,4))
    ax.barh(proj_calendario.Tarea, proj_calendario.dias_inicio_fin, left=proj_calendario.dias_inicio)
    plt.show()




# segundo metodo
# imprime todas las rutas, sus duraciones y si hay mas de una ruta critica
# dibuja los nodos y las aritas, marca en rojo la ruta critica
def encontrar_ruta_critica():
    global entrada_vars
    tareas=[]
    dependencias=[]
    G = nx.DiGraph()

    for i in range(len(entrada_vars)):
        # for j in range(num_columnas):
        nodo = entrada_vars[i][0].get()
        duracion = entrada_vars[i][1].get()
        dependencia = entrada_vars[i][2].get()
        G.add_node(nodo, label=nodo, duration=duracion)
        if dependencia!="":
            dependencia = dependencia.split(",")
            for j in range (len(dependencia)):
                dependencias.append((dependencia[j],nodo))
    G.add_edges_from(dependencias)


    # Encuentra todas las rutas posibles
    all_paths = list(nx.all_simple_paths(G, 'Inicio', 'Fin'))

    # Calcula la duración de cada ruta
    path_durations = []
    print("\nRutas")
    for path in all_paths:
        duration = sum(int(G.nodes[n]['duration']) for n in path)
        path_durations.append((path, duration))
        print("---")
        print(path)
        print(duration)
        print("---")

    # Obtiene la ruta crítica (la de mayor duración)
    critical_path = max(path_durations, key=lambda x: x[1])[0]
    print("\nRuta critica metodo")
    print(critical_path)
    duracion_max=max(path_durations, key=lambda x: x[1])[1]
    print(duracion_max)

    for path in all_paths:
        duration = sum(int(G.nodes[n]['duration']) for n in path)
        if duration==duracion_max and critical_path!=path:
            print("///////")
            print(path)
            print("tambien critica")
            print("////")

    # Dibuja el gráfico
    pos = nx.spring_layout(G, seed=42)
    nx.draw(G, pos, with_labels=False, node_size=1100, node_color='lightblue', font_size=10, font_color='black')

    # Etiqueta los nodos con nombre y duración
    node_labels = {n: f"{G.nodes[n]['label']} ({G.nodes[n]['duration']})" for n in G.nodes}
    nx.draw_networkx_labels(G, pos)

    # Dibuja la ruta crítica con un color diferente
    nx.draw_networkx_edges(G, pos, edgelist=list(zip(critical_path, critical_path[1:])), edge_color='red', width=2)

    # Muestra el gráfico
    plt.title("Gráfico de actividades")
    plt.axis('off')
    plt.show()




def agregarFila():
    global num_filas
    num_filas += 2
    global entrada_vars
    fila_vars = []
    for j in range(num_columnas):
        entrada_var = tk.StringVar()
        caja_entrada = tk.Entry(ventana, textvariable=entrada_var)
        caja_entrada.grid(row=num_filas, column=j+1)
        fila_vars.append(entrada_var)
    entrada_vars.append(fila_vars)


# Crear la ventana principal
ventana = tk.Tk()
ventana.geometry("400x600")
ventana.title("CPM")


# Datos de ejemplo
num_filas = 2
num_columnas = 3

# Lista para almacenar las variables de entrada
entrada_vars = []

etiqueta = tk.Label(ventana, text="Nodo")
etiqueta.grid(row=1, column=1)

etiqueta = tk.Label(ventana, text="Duracion")
etiqueta.grid(row=1, column=2)

etiqueta = tk.Label(ventana, text="Dependencia")
etiqueta.grid(row=1, column=3)


# Crear las cajas de entrada de datos
for i in range(num_filas):
    fila_vars = []
    for j in range(num_columnas):
        entrada_var = tk.StringVar()
        caja_entrada = tk.Entry(ventana, textvariable=entrada_var)
        caja_entrada.grid(row=i+2, column=j+1)
        fila_vars.append(entrada_var)
    entrada_vars.append(fila_vars)

# Botón para guardar los datos
boton_guardar = tk.Button(ventana, text="Guardar", command=guardar_datos)
boton_guardar.grid(row=0, column=1, columnspan=1)

boton_agregar = tk.Button(ventana, text="Agregar", command=agregarFila)
boton_agregar.grid(row=0, column=2, columnspan=1)

# Iniciar el bucle principal de la ventana
ventana.mainloop()
