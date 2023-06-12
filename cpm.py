
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

def guardar_datos():
    global p
    tareas=[]
    dependencias=[]
    for i in range(len(entrada_vars)):
        # for j in range(num_columnas):
        nodo = entrada_vars[i][0].get()
        duracion = entrada_vars[i][1].get()
        dependencia = entrada_vars[i][2].get()
        tareas.append( (nodo,{"duracion":duracion}) )


        # print(f"Dato en la fila {i} columna {j}: {dato}")
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

    print(proj_calendario)
    encontrar_ruta_critica()






def encontrar_ruta_critica():
    # Crear un grafo dirigido
    grafo = nx.DiGraph()
    actividades=[]
    duraciones=[]
    dependencias=[]



    # Agregar nodos y duraciones al grafo
    # for actividad in actividades:
    for i in range(len(entrada_vars)):
        nodo = entrada_vars[i][0].get()
        duracion = entrada_vars[i][1].get()
        dependencia = entrada_vars[i][2].get()
        grafo.add_node(nodo, duracion=int(duracion))
        actividades.append(nodo)
        duraciones.append(duracion)

    # Agregar aristas (dependencias) al grafo
    # for dependencia in dependencias:
    for i in range(len(entrada_vars)):
        nodo = entrada_vars[i][0].get()
        duracion = entrada_vars[i][1].get()
        dependencia = entrada_vars[i][2].get()
        if dependencia!="":
            dependencia = dependencia.split(",")
            for j in range (len(dependencia)):
                grafo.add_edge(dependencia[j],nodo)
                dependencias.append( (nodo,dependencia[j]) )

    # Calcular la ruta crítica
    ruta_critica = nx.algorithms.dag.dag_longest_path(grafo)

    # Calcular la duración total
    # duracion_total = sum(duraciones[actividad] for actividad in ruta_critica)

    # return ruta_critica, duracion_total

        
    # Crear el grafo y resaltar la ruta crítica
    grafo = nx.DiGraph()
    grafo.add_nodes_from(actividades)
    grafo.add_edges_from(dependencias)

    pos = nx.spring_layout(grafo,k=5)

    plt.figure(figsize=(8, 6))
    nx.draw_networkx_nodes(grafo, pos, node_size=500, node_color='lightblue')
    nx.draw_networkx_labels(grafo, pos)
    nx.draw_networkx_edges(grafo, pos, alpha=0.5)

    # Resaltar la ruta crítica en rojo
    ruta_critica_edges = [(ruta_critica[i], ruta_critica[i+1]) for i in range(len(ruta_critica)-1)]
    nx.draw_networkx_edges(grafo, pos, edgelist=ruta_critica_edges, edge_color='red', width=2)

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
ventana.geometry("600x600")

# proyecto nodos
p = Node('proyecto')


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
etiqueta.grid(row=1, column=2)

# Crear las etiquetas de las columnas
# for j in range(num_columnas):
#     etiqueta = tk.Label(ventana, text=f"Columna {j}")
#     etiqueta.grid(row=1, column=j+1)

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
# boton_guardar = tk.Button(ventana, text="Guardar", command=funciones)

boton_guardar.grid(row=0, column=0, columnspan=1)

boton_agregar = tk.Button(ventana, text="Agregar", command=agregarFila)
boton_agregar.grid(row=0, column=1, columnspan=1)

# Iniciar el bucle principal de la ventana
ventana.mainloop()
