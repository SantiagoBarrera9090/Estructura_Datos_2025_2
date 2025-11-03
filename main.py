"""Punto de entrada: carga de CSV, menú y operaciones básicas.

Este módulo contiene la lógica principal: carga de datos, menú interactivo y
orquestación de las operaciones sobre las estructuras de datos. El menú evita
acentos para compatibilidad con consolas en Windows.
"""

import sys  # acceso a argumentos y control del intérprete
import os  # operaciones de sistema de archivos
import csv  # lectura de ficheros CSV
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


# Las funciones de busqueda avanzadas y de rango de fechas se eliminaron
# en esta version para limitar la entrega a las operaciones 0..5.


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
        # Opciones 6..9 fueron eliminadas en esta versión; solo 0..5 permanecen.
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
