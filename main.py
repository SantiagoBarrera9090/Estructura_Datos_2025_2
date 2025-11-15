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
import time  # medición de tiempos para operaciones



def load_csv(path, tree_keyfn=None):
    """Carga un CSV y construye las estructuras de datos principales.

    path: ruta al fichero CSV.
    tree_keyfn: función opcional para extraer la clave usada en el AVLTree.
    Retorna una tupla: (AVLTree, LinkedList, Stack, Queue, stats).
    """
    ll = LinkedList()  # lista con orden original de registros
    stk = Stack()  # pila para demostración LIFO
    q = Queue()  # cola para demostración FIFO
    tree = AVLTree(keyfn=tree_keyfn)  # árbol índice opcional
    count = 0  # contador de registros procesados
    min_date = None  # fecha mínima encontrada
    max_date = None  # fecha máxima encontrada

    # Abrir el CSV en modo lectura, ignorando errores de encoding comunes
    with open(path, encoding="utf-8", errors="ignore") as f:
        reader = csv.reader(f)  # iterador sobre filas CSV
        headers = next(reader, None)  # cabeceras si existen

        # Construir mapa de índices para columnas esperadas
        index = {}  # diccionario de nombre_campo -> índice_columna
        if headers:
            h = [c.strip().lower() for c in headers]  # normalizar cabeceras
            aliases = {
                'customer_id': ['customer id', 'customer_id', 'id'],
                'first_name': ['first name', 'firstname', 'first_name'],
                'last_name': ['last name', 'lastname', 'last_name'],
                'company': ['company', 'company name'],
                'city': ['city'],
                'country': ['country'],
                'email': ['email'],
                'subscription_date': ['subscription date', 'subscription_date', 'date'],
                'website': ['website', 'web'],
            }  # alias de nombres posibles
            for key, names in aliases.items():
                for nm in names:
                    if nm in h:
                        index[key] = h.index(nm)  # asignar índice si existe
                        break

        # Procesar cada fila del CSV
        for row in reader:
            try:
                # Helper local para obtener valor de columna por clave
                def val(k, default=""):
                    if k in index:
                        idx = index[k]
                        if idx < len(row):
                            return row[idx]
                        return default
                    return default

                # Extraer campos según si hay cabeceras detectadas
                if headers and index:
                    cid = val('customer_id', '')
                    fn = val('first_name', '')
                    ln = val('last_name', '')
                    comp = val('company', '')
                    city = val('city', '')
                    country = val('country', '')
                    email = val('email', '')
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



def print_first_n_from_list(ll: LinkedList, n=None):
    # Imprime los primeros `n` registros de una LinkedList.
    # Si n es None, imprime todos los registros.
    i = 0
    for rec in ll:
        if n is not None and i >= n:
            break
        print(str(rec))
        i += 1


def search_by_field_in_tree(tree: AVLTree, field_name, value):
    # Busca registros en un AVLTree por un campo concreto usando predicado
    # Devuelve una LinkedList con los registros que coinciden exactamente
    def pred(r):
        v = getattr(r, field_name, None)  # obtener valor del campo
        if v is None:
            return False
        try:
            return str(v).lower() == str(value).lower()  # comparación case-insensitive
        except Exception:
            return False

    out = LinkedList()  # lista resultado
    for r in tree.find_by_predicate(pred):  # usar predicado del AVLTree
        out.append(r)
    return out


def search_by_field_in_stack(stk: Stack, field_name, value):
    # Busca registros iterando una Stack completa (destructiva)
    # Restaura la pila al estado original después de la búsqueda
    temp_stack = Stack()  # pila temporal para restaurar
    out = LinkedList()  # resultados
    
    # Desapilar todos los elementos buscando coincidencias
    while not stk.is_empty():
        rec = stk.pop()  # extraer elemento
        temp_stack.push(rec)  # guardar para restaurar
        
        v = getattr(rec, field_name, None)
        try:
            if v and str(v).lower() == str(value).lower():
                out.append(rec)  # agregar si coincide
        except Exception:
            continue
    
    # Restaurar pila original
    while not temp_stack.is_empty():
        stk.push(temp_stack.pop())
    
    return out


def search_by_field_in_queue(q: Queue, field_name, value):
    # Busca registros iterando una Queue completa (destructiva)
    # Restaura la cola al estado original después de la búsqueda
    temp_list = LinkedList()  # lista temporal para elementos
    out = LinkedList()  # resultados
    
    # Desencolar todos los elementos
    while not q.is_empty():
        rec = q.dequeue()  # extraer elemento
        temp_list.append(rec)  # guardar para restaurar
        
        v = getattr(rec, field_name, None)
        try:
            if v and str(v).lower() == str(value).lower():
                out.append(rec)  # agregar si coincide
        except Exception:
            continue
    
    # Restaurar cola original
    for rec in temp_list:
        q.enqueue(rec)
    
    return out


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
    print("Menu del sistema de clientes")  # cabecera breve al iniciar
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
        print('\nMenu del sistema de clientes')  # separador visual entre iteraciones
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
            print(f'Ordenado por Customer Id (merge sort). Total registros: {ll.size()}')  # informar resultado
            # mostrar los primeros 10 registros resultantes para que el usuario vea el efecto
            print('\nPrimeros registros despues de ordenar:')
            print_first_n_from_list(ll, 10)  # imprimir un preview de 10 registros
        elif opt == '2' or opt == '3':
            # opciones 2 y 3: 2=First Name (merge), 3=Subscription Date (quick)
            if ll is None:
                print('Primero cargue la base (cargue el archivo al iniciar)')  # verificar datos cargados
                continue
            if opt == '2':
                field = 'first_name'  # ordenar por nombre
                keyfn = lambda r: getattr(r, field, None)
                ll = merge_sort_linkedlist(ll, keyfn)  # merge sort para nombres
                last_sort_field = field
                sort_name = 'First Name (merge sort)'
            else:
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
            print('\nPrimeros registros despues de ordenar:')
            print_first_n_from_list(ll, 10)  # mostrar preview
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
            print('\nPrimeros registros despues de ordenar:')
            print_first_n_from_list(ll, 10)
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
            print_first_n_from_list(ll, n)  # imprimir según elección
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
                
                print(f'\nBuscando "{value}" en campo {field}...')  # informar búsqueda
                
                # Búsqueda en árbol (más eficiente)
                t0 = time.perf_counter()  # tiempo inicial
                results_tree = search_by_field_in_tree(tree, field, value)  # buscar en árbol
                t1 = time.perf_counter()  # tiempo final
                time_tree = t1 - t0  # calcular tiempo
                
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
                
                # Mostrar resultados y tiempos
                print(f'\nResultados encontrados:')  # cabecera resultados
                print(f'Arbol: {results_tree.size()} registros (tiempo: {time_tree:.6f}s)')  # resultados árbol
                print(f'Pila:  {results_stack.size()} registros (tiempo: {time_stack:.6f}s)')  # resultados pila
                print(f'Cola:  {results_queue.size()} registros (tiempo: {time_queue:.6f}s)')  # resultados cola
                
                # Mostrar algunos registros encontrados
                if results_tree.size() > 0:
                    print(f'\nPrimeros registros encontrados:')  # cabecera preview
                    count = 0
                    for r in results_tree:
                        if count >= 5:  # limitar a 5 registros
                            break
                        print(f'  {r}')  # mostrar registro
                        count += 1
                    if results_tree.size() > 5:
                        print(f'  ... y {results_tree.size() - 5} más')
                else:
                    print('No se encontraron registros con ese criterio.')  # no hay resultados
                    
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
                
                print(f'\nBuscando registros entre {d1} y {d2}...')  # informar búsqueda
                
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
                
                # Preview de resultados
                if res_tree.size() > 0:
                    print(f'\nPrimeros registros en el rango:')  # cabecera preview
                    count = 0
                    for r in res_tree:
                        if count >= 3:  # limitar a 3 registros
                            break
                        print(f'  {r}')  # mostrar registro
                        count += 1
                else:
                    print('No hay registros en ese rango de fechas.')  # no hay resultados
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
            print(f'\nTotal de paises: {total_countries}')  # mostrar total
            
            # Crear lista de países con conteos
            class CountryCount:
                def __init__(self, country, count):
                    self.country = country  # nombre país
                    self.count = count  # número clientes
                def __str__(self):
                    return f'{self.country}: {self.count}'  # formato salida
            
            cc_list = LinkedList()  # lista países-conteos
            for key, records in country_idx.items():  # por cada país
                cc_list.append(CountryCount(key, records.size()))  # agregar conteo
            
            # Ordenar por conteo descendente
            cc_sorted = merge_sort_linkedlist(cc_list, keyfn=lambda x: -x.count)  # ordenar desc
            
            # Preguntar cuántos mostrar
            choice = input('Cuantos paises mostrar? (numero o "todos"): ').strip()  # solicitar cantidad
            if choice.lower() in ('todos', 'n', ''):
                to_show = None  # mostrar todos
            else:
                try:
                    to_show = int(choice)  # parsear número
                    if to_show <= 0:
                        to_show = None
                except Exception:
                    print('Entrada invalida, mostrando todos')  # error parsing
                    to_show = None
            
            # Mostrar países y conteos
            print('\nClientes por pais:')  # cabecera
            i = 0
            for item in cc_sorted:  # iterar países ordenados
                if to_show is not None and i >= to_show:  # límite alcanzado
                    break
                print(f'  {item}')  # mostrar país:conteo
                i += 1
            
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
            
            level = 0  # nivel actual
            nodes_in_level = 1  # nodos esperados en nivel
            nodes_printed = 0  # nodos impresos en nivel actual
            
            for key, records in tree_for_last_sort.level_order():  # recorrer por niveles
                if nodes_printed == 0:  # inicio de nuevo nivel
                    print(f'Nivel {level}:')  # cabecera nivel
                
                print(f'  {key} - {records.size()}')  # mostrar nodo
                nodes_printed += 1  # incrementar contador
                
                if nodes_printed >= nodes_in_level:  # nivel completo
                    level += 1  # siguiente nivel
                    nodes_in_level *= 2  # doble nodos en siguiente nivel
                    nodes_printed = 0  # reset contador
                    print()  # línea vacía entre niveles
        elif opt == '0':
            print('Saliendo')
            break
        else:
            print('Opcion no valida')


if __name__ == '__main__':
    if '--test' in sys.argv:
        sample = os.path.join(os.path.dirname(__file__), 'sample.csv')
        if os.path.exists(sample):
            t, ll, s, q, stats = load_csv(sample)
            print('Carga sample:', stats)
            print('Primeros 3 por ID:')
            sorted_ll = merge_sort_linkedlist(ll, lambda r: r.customer_id)
            print_first_n_from_list(sorted_ll, 3)
        else:
            print('No hay sample.csv; ejecuta main sin --test para usar el menu')
    else:
        interactive_menu()
