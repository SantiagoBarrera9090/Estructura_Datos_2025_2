"""Punto de entrada: carga de CSV, menú y operaciones básicas.

Este módulo contiene la lógica principal: carga de datos, menú interactivo y
orquestación de las operaciones sobre las estructuras de datos. El menú evita
acentos para compatibilidad con consolas en Windows.
"""

import sys  # acceso a argumentos y control del intérprete
import os  # operaciones de sistema de archivos
import csv  # lectura de ficheros CSV
import time  # para medir tiempos de ejecución
from datetime import datetime  # para manejo de fechas
from models import Record  # clase Record para representar cada fila del CSV
from structures import LinkedList, Stack, Queue, AVLTree  # estructuras propias del proyecto
from sorting import merge_sort_linkedlist, quick_sort_linkedlist  # algoritmos de ordenamiento locales



def load_csv(path, tree_keyfn=None):
    """Carga un CSV y construye las estructuras de datos principales.

    path: ruta al fichero CSV.
    tree_keyfn: función opcional para extraer la clave usada en el AVLTree.
    Retorna una tupla: (AVLTree, LinkedList, Stack, Queue, stats).
    """
    ll = LinkedList()  # creamos una lista enlazada para mantener el orden original de los datos
    stk = Stack()  # creamos una pila para demostrar funcionamiento LIFO (último en entrar, primero en salir)
    q = Queue()  # creamos una cola para demostrar funcionamiento FIFO (primero en entrar, primero en salir)
    tree = AVLTree(keyfn=tree_keyfn)  # creamos un árbol balanceado para búsquedas rápidas
    count = 0  # contador para saber cuántos registros hemos procesado
    min_date = None  # guardaremos la fecha de suscripción más antigua que encontremos
    max_date = None  # guardaremos la fecha de suscripción más reciente que encontremos

    # abrimos el archivo CSV para lectura, ignorando caracteres problemáticos
    with open(path, encoding="utf-8", errors="ignore") as f:
        reader = csv.reader(f)  # creamos un lector que nos dará una fila a la vez
        headers = next(reader, None)  # intentamos leer la primera fila como cabeceras

        # construimos un mapa para encontrar las columnas del CSV por su nombre
        index = {}  # diccionario que nos dirá en qué columna está cada campo
        if headers:  # si encontramos cabeceras en la primera fila
            h = [c.strip().lower() for c in headers]  # limpiamos y convertimos a minúsculas
            aliases = {  # definimos los nombres posibles para cada campo
                'customer_id': ['customer id', 'customer_id', 'id'],  # diferentes formas de nombrar el ID
                'first_name': ['first name', 'firstname', 'first_name'],  # diferentes formas del nombre
                'last_name': ['last name', 'lastname', 'last_name'],  # diferentes formas del apellido
                'company': ['company', 'company name'],  # diferentes formas de la empresa
                'city': ['city'],  # nombre de la ciudad
                'country': ['country'],  # nombre del país
                'email': ['email'],  # correo electrónico
                'subscription_date': ['subscription date', 'subscription_date', 'date'],  # fecha de suscripción
                'website': ['website', 'web'],  # página web
            }  # estos alias nos ayudan a ser flexibles con los nombres de columnas
            for key, names in aliases.items():  # por cada campo que necesitamos
                for nm in names:  # probamos cada nombre posible
                    if nm in h:  # si encontramos este nombre en las cabeceras
                        index[key] = h.index(nm)  # guardamos en qué columna está
                        break  # no necesitamos seguir buscando

        # procesamos cada fila de datos del CSV una por una
        for row in reader:  # por cada línea que quede en el archivo
            try:  # intentamos procesar esta fila, si falla la saltamos
                # función auxiliar para obtener el valor de una columna de forma segura
                def val(k, default=""):  # k es el nombre del campo, default es qué devolver si no existe
                    if k in index:  # si sabemos dónde está esta columna
                        idx = index[k]  # obtenemos el número de columna
                        if idx < len(row):  # si la fila tiene suficientes columnas
                            return row[idx]  # devolvemos el valor de esa columna
                        return default  # si no hay suficientes columnas, devolvemos el valor por defecto
                    return default  # si no conocemos esta columna, devolvemos el valor por defecto

                # extraemos los valores de cada campo dependiendo de si tenemos cabeceras
                if headers and index:  # si detectamos cabeceras y tenemos el mapa de columnas
                    cid = val('customer_id', '')  # obtenemos el ID del cliente
                    fn = val('first_name', '')  # obtenemos el primer nombre
                    ln = val('last_name', '')  # obtenemos el apellido
                    comp = val('company', '')  # obtenemos el nombre de la empresa
                    city = val('city', '')  # obtenemos la ciudad
                    country = val('country', '')  # obtenemos el país
                    email = val('email', '')  # obtenemos el correo electrónico
                    sub = val('subscription_date', '')
                    web = val('website', '')
                else:
                    # si no hay cabecera, rellenar hasta 9 campos y tomar los primeros
                    row = row + [''] * 9
                    cid, fn, ln, comp, city, country, email, sub, web = row[:9]

                # Construir el objeto Record con limpieza de espacios
                rec = Record(
                    cid.strip(), fn.strip(), ln.strip(), comp.strip(),
                    city.strip(), country.strip(), email.strip(),
                    sub.strip(), web.strip(),
                )
            except Exception:
                # Si la fila no se puede parsear, saltarla
                continue

            # Agregar registros a las estructuras propias
            ll.append(rec)  # conservar orden original
            stk.push(rec)  # añadir a la pila
            q.enqueue(rec)  # añadir a la cola
            tree.insert(rec)  # indexar en el AVLTree
            count += 1  # incrementar contador

            # Actualizar min/max de suscripción si está presente
            if rec.subscription_date:
                if (min_date is None) or (rec.subscription_date < min_date):
                    min_date = rec.subscription_date
                if (max_date is None) or (rec.subscription_date > max_date):
                    max_date = rec.subscription_date

    stats = {'count': count, 'min_date': min_date, 'max_date': max_date}  # paquete de estadísticas
    return tree, ll, stk, q, stats



def print_first_n_from_list(ll: LinkedList, n=None, sort_info=None):
    # Esta función muestra todos los registros adaptandose al tamaño de la base de datos
    # Optimizada para manejar desde 100 hasta millones de registros
    if ll is None or ll.size() == 0:
        print('No hay datos para mostrar en la base de datos.')  # si no hay información
        return
    
    total_records = ll.size()  # obtenemos el total para optimizar
    
    # determinamos cuántos registros vamos a mostrar
    if n is None:  # si no especificaron cantidad, mostramos todos
        records_to_show = total_records
        if sort_info:
            print(f'Mostrando todos los {total_records:,} registros ordenados por {sort_info}:')  # incluir criterio
        else:
            print(f'Mostrando todos los {total_records:,} registros de la base de datos:')  # formato original
    else:  # si especificaron una cantidad
        records_to_show = min(n, total_records)  # no podemos mostrar más de los que tenemos
        if sort_info:
            print(f'Mostrando los primeros {records_to_show:,} de {total_records:,} registros ordenados por {sort_info}:')  # incluir criterio
        else:
            print(f'Mostrando los primeros {records_to_show:,} de {total_records:,} registros de la base de datos:')  # formato original
    
    print('=' * 100)  # línea separadora más visible
    
    i = 0  # llevamos la cuenta de cuántos hemos mostrado
    start_time = time.time()  # medimos tiempo para bases grandes
    
    for rec in ll:  # recorremos cada registro
        if i >= records_to_show:  # si ya mostramos la cantidad solicitada
            break  # paramos aquí
        i += 1  # aumentamos el contador
        print(f'{i:8,d}: {str(rec)}')  # formato con comas para números grandes
        
        # mostrar progreso cada 1000 registros en bases grandes (solo si mostramos muchos)
        if records_to_show > 1000 and i % 1000 == 0:
            elapsed = time.time() - start_time
            print(f'[PROGRESO: {i:,}/{records_to_show:,} registros mostrados - {elapsed:.1f}s transcurridos]')
    
    elapsed_total = time.time() - start_time
    print('=' * 100)  # línea separadora final
    if n is None:  # si mostramos todos
        if sort_info:
            print(f'RESUMEN: {i:,} registros ordenados por {sort_info} mostrados completamente en {elapsed_total:.2f} segundos')  # incluir criterio
        else:
            print(f'RESUMEN: {i:,} registros mostrados completamente en {elapsed_total:.2f} segundos')  # resumen original
    else:  # si mostramos solo una cantidad limitada
        if sort_info:
            print(f'RESUMEN: {i:,} de {total_records:,} registros ordenados por {sort_info} mostrados en {elapsed_total:.2f} segundos')  # incluir criterio
        else:
            print(f'RESUMEN: {i:,} de {total_records:,} registros mostrados en {elapsed_total:.2f} segundos')  # resumen original


def search_by_field_in_tree(tree: AVLTree, field_name, value):
    # Esta función busca clientes en el árbol binario por cualquier campo específico
    # Es muy eficiente porque aprovecha la estructura del árbol para buscar rápidamente
    def pred(r):
        v = getattr(r, field_name, None)  # extraemos el valor del campo que nos interesa del registro
        if v is None:  # si el campo no existe o está vacío
            return False  # este registro no nos sirve
        try:
            return str(v).lower() == str(value).lower()  # comparamos ignorando mayúsculas y minúsculas
        except Exception:  # por si hay algún problema con la conversión
            return False  # mejor no incluir este registro

    out = LinkedList()  # creamos una lista nueva para guardar todos los resultados
    for r in tree.find_by_predicate(pred):  # le pedimos al árbol que nos dé todos los que cumplen la condición
        out.append(r)  # agregamos cada resultado a nuestra lista
    return out  # devolvemos todos los registros que encontramos


def search_by_field_in_stack(stk: Stack, field_name, value):
    # Esta función busca en la pila pero es más lenta que el árbol
    # Tiene que revisar elemento por elemento desde arriba hasta abajo
    temp_stack = Stack()  # necesitamos otra pila para no perder los datos originales
    out = LinkedList()  # aquí vamos guardando lo que encontramos
    
    # Sacamos todos los elementos de la pila original para revisarlos
    while not stk.is_empty():  # mientras queden elementos por revisar
        rec = stk.pop()  # sacamos el que está arriba
        temp_stack.push(rec)  # lo guardamos en la pila temporal para no perderlo
        
        v = getattr(rec, field_name, None)  # obtenemos el valor del campo a buscar
        try:
            if v and str(v).lower() == str(value).lower():  # si coincide con lo que buscamos
                out.append(rec)  # lo agregamos a los resultados
        except Exception:  # si hay algún error
            continue  # seguimos con el siguiente
    
    # Ahora devolvemos todos los elementos a la pila original como estaban
    while not temp_stack.is_empty():  # mientras tengamos elementos guardados
        stk.push(temp_stack.pop())  # los devolvemos a la pila original
    
    return out  # regresamos todos los resultados encontrados


def search_by_field_in_queue(q: Queue, field_name, value):
    # Esta función busca en la cola, también es lenta como la pila
    # La diferencia es que revisamos desde el primero hasta el último
    temp_list = LinkedList()  # usamos una lista temporal para guardar todo
    out = LinkedList()  # aquí ponemos los resultados de la búsqueda
    
    # Sacamos todos los elementos de la cola para revisarlos
    while not q.is_empty():  # mientras haya elementos en la cola
        rec = q.dequeue()  # sacamos el primero de la fila
        temp_list.append(rec)  # lo guardamos para no perderlo
        
        v = getattr(rec, field_name, None)  # obtenemos el valor del campo
        try:
            if v and str(v).lower() == str(value).lower():  # si es lo que buscamos
                out.append(rec)  # lo agregamos a los resultados
        except Exception:  # si algo sale mal
            continue  # continuamos con el siguiente elemento
    
    # Regresamos todos los elementos a la cola en el mismo orden
    for rec in temp_list:  # por cada elemento que guardamos
        q.enqueue(rec)  # lo volvemos a meter a la cola
    
    return out  # devolvemos todo lo que encontramos


def search_by_date_range(tree_or_structure, start_date, end_date):
    # Busca registros por rango de fechas de suscripción
    # Acepta AVLTree, Stack, Queue o LinkedList
    out = LinkedList()  # resultados

    def check(r):
        if not r.subscription_date:  # si no tiene fecha
            return False
        return start_date <= r.subscription_date <= end_date  # verificar rango

    if hasattr(tree_or_structure, 'find_by_predicate'):  # es AVLTree
        for r in tree_or_structure.find_by_predicate(check):
            out.append(r)
    elif isinstance(tree_or_structure, Stack):  # es Stack
        temp_stack = Stack()
        while not tree_or_structure.is_empty():
            rec = tree_or_structure.pop()
            temp_stack.push(rec)
            if check(rec):
                out.append(rec)
        # Restaurar stack
        while not temp_stack.is_empty():
            tree_or_structure.push(temp_stack.pop())
    elif isinstance(tree_or_structure, Queue):  # es Queue
        temp_list = LinkedList()
        while not tree_or_structure.is_empty():
            rec = tree_or_structure.dequeue()
            temp_list.append(rec)
            if check(rec):
                out.append(rec)
        # Restaurar queue
        for rec in temp_list:
            tree_or_structure.enqueue(rec)
    else:  # es LinkedList u otra estructura iterable
        for r in tree_or_structure:
            if check(r):
                out.append(r)
    return out


def interactive_menu():
    # Menu interactivo principal.
    # Solo las opciones 0..5 estan operativas en esta version. Las demas se reservan.
    print("Sistema de Gestión de Clientes - Escalable para cualquier volumen de datos")  # cabecera mejorada
    tree = None
    ll = None
    stk = None
    q = None
    stats = None
    # indices secundarios por campo (construidos bajo demanda)
    indices = {}
    # ultimo orden aplicado (campo)
    last_sort_field = None
    # arbol construido con la clave del ultimo orden (para opcion 8)
    tree_for_last_sort = None
    tree_for_last_sort = None

    # si existe BusinessData.csv en el folder, preguntamos si cargarla al inicio
    default_csv = os.path.join(os.path.dirname(__file__), 'BusinessData.csv')  # ruta por defecto
    if os.path.exists(default_csv):  # comprobar existencia de fichero
        ans = input(f"Se encontro 'BusinessData.csv' en el proyecto. Cargarla ahora? (s/n): ").strip().lower()  # solicitar confirmación
        if ans == 's':
            tree, ll, stk, q, stats = load_csv(default_csv)  # cargar CSV predeterminado
            print(f'Cargados {stats["count"]} registros. Fecha min: {stats["min_date"]} max: {stats["max_date"]}')  # mostrar resumen
    while True:
        # Mostrar información dinámica del sistema
        if ll is not None:
            print(f'\nSistema de Clientes - Base de datos cargada: {ll.size():,} registros')  # información dinámica
        else:
            print('\nSistema de Clientes - Listo para cargar cualquier volumen de datos')  # mensaje inicial
        print('1. Ordenar por Customer Id')  # opción 1: ordenar por id
        print('2. Ordenar por First Name')  # opción 2: ordenar por nombre
        print('3. Ordenar por Subscription Date')  # opción 3: ordenar por fecha
        print('4. Ordenar por Country')  # opción 4: ordenar por país
        print('5. Mostrar primeros n registros ordenados con todos sus datos o todos los registros')  # opción 5: mostrar registros
        print('   (El menu preguntara el numero de registros o una opcion para mostrarlos todos)')  # aclaración para opción 5
        print('6. Buscar cliente por First Name, Last Name, Company, rango de fechas de suscripcion o Country')  # opción 6: búsquedas
        print('   (Se mostraran los tiempos de busqueda usando el arbol y usando la pila/cola)')  # aclaración tiempos
        print('7. Mostrar estadisticas basicas')  # opción 7: estadísticas
        print('8. Mostrar arbol binario')  # opción 8: visualización árbol
        print('0. Salir')  # opción 0: salir del programa
        opt = input('Seleccione una opcion: ').strip()  # leer la opción seleccionada por el usuario
        if opt == '1':
            # Ordenar por Customer Id
            if ll is None:
                print('Primero cargue la base (cargue el archivo al iniciar)')  # indicar que no hay datos cargados
                continue
            field = 'customer_id'  # campo a usar como clave
            keyfn = lambda r: getattr(r, field, None)  # función que extrae la clave de un record
            # usamos MergeSort por defecto
            ll = merge_sort_linkedlist(ll, keyfn)  # ordenar la linked list usando merge sort
            last_sort_field = field  # recordar último campo usado para ordenar
            # construyo arbol indexado por este campo para opcion 8
            tree_for_last_sort = AVLTree(keyfn=lambda r: getattr(r, field, None))  # nuevo árbol índice
            for rec in ll:
                tree_for_last_sort.insert(rec)  # poblar árbol con registros ordenados
            print(f'Ordenado por Customer Id (merge sort). Total registros: {ll.size()}')  # informar resultado completo
            # mostrar todos los registros resultantes para verificar el ordenamiento completo
            print('\nTodos los registros despues de ordenar por Customer ID:')
            print_first_n_from_list(ll, None, 'Customer ID (merge sort)')  # incluir información del ordenamiento
        elif opt == '2':
            # Ordenar por First Name usando merge sort
            if ll is None:
                print('Primero cargue la base (cargue el archivo al iniciar)')  # verificar datos cargados
                continue
            field = 'first_name'  # ordenar por nombre
            keyfn = lambda r: getattr(r, field, None)
            ll = merge_sort_linkedlist(ll, keyfn)  # merge sort para nombres
            last_sort_field = field
            sort_name = 'First Name (merge sort)'
            # construyo tambien el arbol para la opcion 8
            tree_for_last_sort = AVLTree(keyfn=lambda r: getattr(r, field, None))
            for rec in ll:
                tree_for_last_sort.insert(rec)  # poblar índice con orden actual
            print(f'Ordenado por {sort_name}. Total registros: {ll.size()}')
            print('\nTodos los registros despues de ordenar por First Name:')
            print_first_n_from_list(ll, None, sort_name)  # mostrar con información de ordenamiento
        elif opt == '3':
            # Ordenar por Subscription Date usando quick sort
            if ll is None:
                print('Primero cargue la base (cargue el archivo al iniciar)')  # verificar datos cargados
                continue
            field = 'subscription_date'  # ordenar por fecha de suscripción
            keyfn = lambda r: getattr(r, field, None)
            ll = quick_sort_linkedlist(ll, keyfn)  # quick sort para fechas
            last_sort_field = field
            sort_name = 'Subscription Date (quick sort)'
            # construyo tambien el arbol para la opcion 8
            tree_for_last_sort = AVLTree(keyfn=lambda r: getattr(r, field, None))
            for rec in ll:
                tree_for_last_sort.insert(rec)  # poblar índice con orden actual
            print(f'Ordenado por {sort_name}. Total registros: {ll.size()}')
            print('\nTodos los registros despues de ordenar por Subscription Date:')
            print_first_n_from_list(ll, None, sort_name)  # mostrar con información de ordenamiento
        elif opt == '4':
            # Ordenar por Country
            if ll is None:
                print('Primero cargue la base (cargue el archivo al iniciar)')  # comprobar datos cargados
                continue
            field = 'country'  # campo país
            keyfn = lambda r: getattr(r, field, None)
            ll = merge_sort_linkedlist(ll, keyfn)  # ordenar por país
            last_sort_field = field
            tree_for_last_sort = AVLTree(keyfn=lambda r: getattr(r, field, None))
            for rec in ll:
                tree_for_last_sort.insert(rec)
            print(f'Ordenado por Country (merge sort). Total registros: {ll.size()}')
            print('\nTodos los registros despues de ordenar por pais:')
            print_first_n_from_list(ll, None, 'Country (merge sort)')  # incluir información del ordenamiento
        elif opt == '5':
            # Mostrar primeros n registros o todos
            if ll is None:
                print('Primero cargue la base (opcion 9)')  # nota: instrucción anterior al recorte de opciones
                continue
            s = input("Ingrese numero de registros o 'todos' para mostrarlos todos: ").strip().lower()  # pedir cantidad
            if s == 'todos' or s == '' or s == 't':
                n = None  # mostrar todos
            else:
                try:
                    n = int(s)  # intentar parsear número
                    if n <= 0:
                        n = None
                except Exception:
                    print('Entrada invalida, mostrando todos')
                    n = None
            # Determinar información del último ordenamiento
            if last_sort_field:
                sort_methods = {
                    'customer_id': 'Customer ID (merge sort)',
                    'first_name': 'First Name (merge sort)', 
                    'subscription_date': 'Subscription Date (quick sort)',
                    'country': 'Country (merge sort)'
                }
                sort_info = sort_methods.get(last_sort_field, f'{last_sort_field} (ordenamiento aplicado)')
            else:
                sort_info = None
            print_first_n_from_list(ll, n, sort_info)  # imprimir con información de ordenamiento
        elif opt == '6':
            # Buscar cliente por varios campos con comparación de tiempos
            if ll is None or tree is None or stk is None or q is None:
                print('Primero cargue la base (cargue el archivo al iniciar)')  # verificar datos
                continue
            
            choice = input('Buscar por (1)first_name (2)last_name (3)company (4)country (5)rango_fechas: ').strip()  # tipo búsqueda
            
            if choice in ('1','2','3','4'):  # búsqueda por campo
                field_map = {'1':'first_name','2':'last_name','3':'company','4':'country'}  # mapeo opción->campo
                field = field_map[choice]
                value = input(f'Valor para {field}: ').strip()  # valor a buscar
                
                print(f'\\nBuscando "{value}" en campo {field} en base de datos de {ll.size():,} registros...')  # informar tamaño
                
                # Búsqueda en árbol (más eficiente para cualquier tamaño)
                t0 = time.perf_counter()  # tiempo inicial con alta precisión
                results_tree = search_by_field_in_tree(tree, field, value)  # buscar en árbol
                t1 = time.perf_counter()  # tiempo final
                time_tree = t1 - t0  # calcular tiempo exacto
                
                # Búsqueda en pila (menos eficiente)
                t2 = time.perf_counter()
                results_stack = search_by_field_in_stack(stk, field, value)  # buscar en pila
                t3 = time.perf_counter()
                time_stack = t3 - t2
                
                # Búsqueda en cola (menos eficiente)
                t4 = time.perf_counter()
                results_queue = search_by_field_in_queue(q, field, value)  # buscar en cola
                t5 = time.perf_counter()
                time_queue = t5 - t4
                
                # Mostrar resultados y tiempos con formato optimizado
                print(f'\\nResultados de búsqueda en base de {ll.size():,} registros:')  # cabecera con tamaño
                print(f'Arbol: {results_tree.size():,} registros encontrados (tiempo: {time_tree:.6f}s)')  # formato con comas
                print(f'Pila:  {results_stack.size():,} registros encontrados (tiempo: {time_stack:.6f}s)')  # formato con comas
                print(f'Cola:  {results_queue.size():,} registros encontrados (tiempo: {time_queue:.6f}s)')  # formato con comas
                
                # Mostrar eficiencia relativa
                if time_stack > 0 and time_tree > 0:
                    efficiency = time_stack / time_tree
                    print(f'\\nEficiencia: El árbol es {efficiency:.1f}x más rápido que estructuras lineales')
                
                # Mostrar todos los registros encontrados sin limitaciones
                if results_tree.size() > 0:
                    print(f'\nTodos los registros encontrados en la búsqueda:')  # mostrar resultados completos
                    for r in results_tree:  # iterar sobre todos los resultados
                        print(f'  {r}')  # imprimir cada registro encontrado
                    print(f'\nTotal de coincidencias: {results_tree.size()} registros')  # resumen final
                else:
                    print('No se encontraron registros con ese criterio en toda la base de datos.')  # búsqueda exhaustiva sin resultados
                    
            elif choice == '5':  # búsqueda por rango de fechas
                fmt = '%Y-%m-%d'  # formato fecha esperado
                s1 = input('Fecha inicio (YYYY-MM-DD): ').strip()  # fecha inicio
                s2 = input('Fecha fin (YYYY-MM-DD): ').strip()  # fecha fin
                try:
                    d1 = datetime.strptime(s1, fmt).date()  # parsear fecha inicio
                    d2 = datetime.strptime(s2, fmt).date()  # parsear fecha fin
                except Exception:
                    print('Formato de fecha invalido')  # error formato
                    continue
                
                print(f'\nBuscando registros entre {d1} y {d2} en base de {ll.size():,} registros...')  # informar búsqueda con tamaño
                
                # Búsqueda en árbol
                t0 = time.perf_counter()
                res_tree = search_by_date_range(tree, d1, d2)  # buscar en árbol
                t1 = time.perf_counter()
                time_tree = t1 - t0
                
                # Búsqueda en pila
                t2 = time.perf_counter()
                res_stack = search_by_date_range(stk, d1, d2)  # buscar en pila
                t3 = time.perf_counter()
                time_stack = t3 - t2
                
                # Búsqueda en cola
                t4 = time.perf_counter()
                res_queue = search_by_date_range(q, d1, d2)  # buscar en cola
                t5 = time.perf_counter()
                time_queue = t5 - t4
                
                # Mostrar resultados
                print(f'\nRegistros en rango de fechas:')  # cabecera resultados
                print(f'Arbol: {res_tree.size()} registros (tiempo: {time_tree:.6f}s)')  # resultados árbol
                print(f'Pila:  {res_stack.size()} registros (tiempo: {time_stack:.6f}s)')  # resultados pila
                print(f'Cola:  {res_queue.size()} registros (tiempo: {time_queue:.6f}s)')  # resultados cola
                
                # Mostrar todos los resultados del rango de fechas
                if res_tree.size() > 0:
                    print(f'\nTodos los registros en el rango de fechas {d1} a {d2}:')  # mostrar rango completo
                    for r in res_tree:  # mostrar cada registro del rango
                        print(f'  {r}')  # imprimir registro completo
                    print(f'\nTotal de registros en el rango: {res_tree.size()}')  # conteo final
                else:
                    print('No hay registros en ese rango de fechas en toda la base de datos.')  # búsqueda completa sin resultados
            else:
                print('Opcion de busqueda no valida.')  # opción inválida
                
        elif opt == '7':
            # Mostrar estadísticas básicas
            if ll is None or stats is None:
                print('Primero cargue la base (cargue el archivo al iniciar)')  # verificar datos
                continue
            
            # Construir índice por país si no existe
            if 'country' not in indices:
                print('Construyendo indice por pais...')  # informar construcción
                idx = AVLTree(keyfn=lambda r: getattr(r, 'country', None))  # crear índice
                for rec in ll:  # poblar índice
                    idx.insert(rec)
                indices['country'] = idx  # guardar índice
                print('Indice construido.')  # confirmar
            
            country_idx = indices['country']  # obtener índice
            
            # Contar países únicos
            total_countries = 0  # contador países
            for _ in country_idx.items():  # iterar claves únicas
                total_countries += 1
            print(f'\\nEstadísticas de base de datos con {ll.size():,} registros:')  # contexto de tamaño
            print(f'Total de países diferentes: {total_countries:,}')  # formato con comas
            
            # Crear lista de países con conteos optimizada
            class CountryCount:
                def __init__(self, country, count):
                    self.country = country  # nombre país
                    self.count = count  # número clientes
                def __str__(self):
                    return f'{self.country}: {self.count:,} clientes'  # formato con comas para números grandes
            
            cc_list = LinkedList()  # lista países-conteos
            for key, records in country_idx.items():  # por cada país
                cc_list.append(CountryCount(key, records.size()))  # agregar conteo
            
            # Ordenar por conteo descendente
            cc_sorted = merge_sort_linkedlist(cc_list, keyfn=lambda x: -x.count)  # ordenar desc
            
            # Mostramos todos los países sin preguntar porque queremos información completa
            print('\nTodos los clientes por pais (ordenados de mayor a menor):')  # mostrar todo
            
            # Recorremos y mostramos cada país con su cantidad de clientes
            for item in cc_sorted:  # por cada país en orden descendente
                print(f'  {item}')  # mostramos el país y cuántos clientes tiene
            
            print(f'\nResumen completo: {cc_sorted.size()} paises diferentes en total')  # resumen final
            
            # Mostrar fechas extremas
            if stats['min_date'] and stats['max_date']:  # si hay fechas
                print(f'\nFecha mas antigua: {stats["min_date"]}')  # fecha mínima
                print(f'Fecha mas reciente: {stats["max_date"]}')  # fecha máxima
            else:
                print('\nNo hay fechas de suscripcion validas en los datos.')  # sin fechas
                
        elif opt == '8':
            # Mostrar árbol binario por niveles
            if tree_for_last_sort is None:
                print('No hay criterio de orden aplicado aun. Ordene por algun campo primero (opciones 1-4).')  # sin orden
                continue
            
            print(f'\nArbol binario por niveles (ordenado por {last_sort_field}):')  # cabecera
            print('Formato: clave - numero_de_registros')  # formato explicación
            print('----------------------------------------')  # separador
            
            level = 0  # empezamos desde el nivel 0 (la raíz)
            nodes_in_level = 1  # en el primer nivel solo hay un nodo
            nodes_printed = 0  # contador de nodos que hemos mostrado en este nivel
            total_nodes = 0  # contador total de nodos en el árbol
            
            # Recorremos todo el árbol nivel por nivel sin limitaciones
            for key, records in tree_for_last_sort.level_order():  # obtenemos cada nodo por niveles
                if nodes_printed == 0:  # si es el primer nodo del nivel
                    print(f'Nivel {level}:')  # mostramos qué nivel estamos viendo
                
                print(f'  {key} - {records.size()} registros')  # mostramos la clave y cuántos registros tiene
                nodes_printed += 1  # contamos que ya mostramos este nodo
                total_nodes += 1  # contamos el nodo total
                
                if nodes_printed >= nodes_in_level:  # si ya mostramos todos los nodos de este nivel
                    level += 1  # pasamos al siguiente nivel
                    nodes_in_level *= 2  # el siguiente nivel puede tener el doble de nodos
                    nodes_printed = 0  # reiniciamos el contador del nivel
                    print()  # dejamos una línea en blanco para separar niveles
            
            print(f'\nArbol completo: {total_nodes:,} nodos distribuidos en {level + 1} niveles')  # resumen con formato
        elif opt == '0':
            print('Saliendo')
            break
        else:
            print('Opcion no valida')


if __name__ == '__main__':  # esta línea se ejecuta solo cuando corremos este archivo directamente
    if '--test' in sys.argv:  # si el usuario pasó el parámetro --test al ejecutar
        sample = os.path.join(os.path.dirname(__file__), 'sample.csv')  # buscamos un archivo de prueba
        if os.path.exists(sample):  # si existe el archivo de muestra
            t, ll, s, q, stats = load_csv(sample)  # cargamos los datos de prueba
            print('Carga sample:', stats)  # mostramos las estadísticas de la carga
            print('Primeros 3 por ID:')  # anunciamos que vamos a mostrar los primeros 3
            sorted_ll = merge_sort_linkedlist(ll, lambda r: r.customer_id)  # ordenamos por ID
            print_first_n_from_list(sorted_ll, 3)  # mostramos solo los primeros 3 registros
        else:  # si no existe el archivo de prueba
            print('No hay sample.csv; ejecuta main sin --test para usar el menu')  # informamos al usuario
    else:  # si no se pasó --test (ejecución normal)
        interactive_menu()  # iniciamos el menú interactivo principal
