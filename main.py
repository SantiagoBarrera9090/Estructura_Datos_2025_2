"""Punto de entrada: carga de CSV, menu basico y operaciones solicitadas.

Comentarios estilo estudiante colombiano: aqui tenemos lo minimo viable para
cargar los datos y probar ordenamientos y busquedas. El menu evita acentos para
no pelear con la consola de Windows.
"""

import sys
import os
import csv
from models import Record
from structures import LinkedList, Stack, Queue, AVLTree
from sorting import merge_sort_linkedlist, quick_sort_linkedlist
import time


def load_csv(path, tree_keyfn=None):
    """Lee CSV y carga en AVLTree y en LinkedList (orden original).

    Resultado: (avl_tree, linkedlist, stack, queue, stats)
    """
    ll = LinkedList()
    stk = Stack()
    q = Queue()
    tree = AVLTree(keyfn=tree_keyfn)
    count = 0
    min_date = None
    max_date = None

    with open(path, encoding="utf-8", errors="ignore") as f:
        reader = csv.reader(f)
        headers = next(reader, None)

        # preparo un mapeo de indices (solo una vez)
        index = {}
        if headers:
            h = [c.strip().lower() for c in headers]
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
            }
            for key, names in aliases.items():
                for nm in names:
                    if nm in h:
                        index[key] = h.index(nm)
                        break

        for row in reader:
            try:
                def val(k, default=""):
                    if k in index:
                        idx = index[k]
                        if idx < len(row):
                            return row[idx]
                        return default
                    return default

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
                    row = row + [''] * 9
                    cid, fn, ln, comp, city, country, email, sub, web = row[:9]

                rec = Record(
                    cid.strip(),
                    fn.strip(),
                    ln.strip(),
                    comp.strip(),
                    city.strip(),
                    country.strip(),
                    email.strip(),
                    sub.strip(),
                    web.strip(),
                )
            except Exception:
                continue

            ll.append(rec)
            stk.push(rec)
            q.enqueue(rec)
            tree.insert(rec)
            count += 1

            if rec.subscription_date:
                if (min_date is None) or (rec.subscription_date < min_date):
                    min_date = rec.subscription_date
                if (max_date is None) or (rec.subscription_date > max_date):
                    max_date = rec.subscription_date

    stats = {'count': count, 'min_date': min_date, 'max_date': max_date}
    return tree, ll, stk, q, stats


def print_first_n_from_list(ll: LinkedList, n=None):
    i = 0
    for rec in ll:
        if n is not None and i >= n:
            break
        print(str(rec))
        i += 1


def search_by_field_in_tree(tree: AVLTree, field_name, value):
    def pred(r):
        v = getattr(r, field_name, None)
        if v is None:
            return False
        try:
            return str(v).lower() == str(value).lower()
        except Exception:
            return False

    return list(tree.find_by_predicate(pred))


def search_by_field_in_list(ll: LinkedList, field_name, value):
    out = []
    for r in ll:
        v = getattr(r, field_name, None)
        try:
            if v and str(v).lower() == str(value).lower():
                out.append(r)
        except Exception:
            continue
    return out


def search_by_date_range(tree_or_list, start_date, end_date):
    out = []

    def check(r):
        if not r.subscription_date:
            return False
        return start_date <= r.subscription_date <= end_date

    if hasattr(tree_or_list, 'find_by_predicate'):
        for r in tree_or_list.find_by_predicate(check):
            out.append(r)
    else:
        for r in tree_or_list:
            if check(r):
                out.append(r)
    return out


def interactive_menu():
    print("Menu del sistema de clientes")
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
    default_csv = os.path.join(os.path.dirname(__file__), 'BusinessData.csv')
    if os.path.exists(default_csv):
        ans = input(f"Se encontro 'BusinessData.csv' en el proyecto. Cargarla ahora? (s/n): ").strip().lower()
        if ans == 's':
            tree, ll, stk, q, stats = load_csv(default_csv)
            print(f'Cargados {stats["count"]} registros. Fecha min: {stats["min_date"]} max: {stats["max_date"]}')
    while True:
        print('\nMenu del sistema de clientes')
        print('1. Ordenar por Customer Id')
        print('2. Ordenar por First Name')
        print('3. Ordenar por Subscription Date')
        print('4. Ordenar por Country')
        print('5. Mostrar primeros n registros ordenados con todos sus datos o todos los registros')
        print('   (El menu preguntara el numero de registros o una opcion para mostrarlos todos)')
        print('6. Buscar cliente por First Name, Last Name, Company, rango de fechas de suscripcion o Country')
        print('   (Se mostraran los tiempos de busqueda usando el arbol y usando la pila/cola)')
        print('7. Mostrar estadisticas basicas')
        print('8. Mostrar arbol binario')
        print('0. Salir')
        opt = input('Seleccione una opcion: ').strip()
        if opt == '1':
            # Ordenar por Customer Id
            if ll is None:
                print('Primero cargue la base (opcion 9)')
                continue
            field = 'customer_id'
            keyfn = lambda r: getattr(r, field, None)
            # usamos MergeSort por defecto
            ll = merge_sort_linkedlist(ll, keyfn)
            last_sort_field = field
            # construyo arbol indexado por este campo para opcion 8
            tree_for_last_sort = AVLTree(keyfn=lambda r: getattr(r, field, None))
            for rec in ll:
                tree_for_last_sort.insert(rec)
            print(f'Ordenado por Customer Id (merge sort). Total registros: {len(list(ll))}')
            # mostrar los primeros 10 registros resultantes para que el usuario vea el efecto
            print('\nPrimeros registros despues de ordenar:')
            print_first_n_from_list(ll, 10)
        elif opt == '2' or opt == '3':
            # opciones 2 y 3: 2=First Name (merge), 3=Subscription Date (quick)
            if ll is None:
                print('Primero cargue la base (opcion 9)')
                continue
            if opt == '2':
                field = 'first_name'
                keyfn = lambda r: getattr(r, field, None)
                ll = merge_sort_linkedlist(ll, keyfn)
                last_sort_field = field
                sort_name = 'First Name (merge sort)'
            else:
                field = 'subscription_date'
                keyfn = lambda r: getattr(r, field, None)
                ll = quick_sort_linkedlist(ll, keyfn)
                last_sort_field = field
                sort_name = 'Subscription Date (quick sort)'
            # construyo tambien el arbol para la opcion 8
            tree_for_last_sort = AVLTree(keyfn=lambda r: getattr(r, field, None))
            for rec in ll:
                tree_for_last_sort.insert(rec)
            print(f'Ordenado por {sort_name}. Total registros: {len(list(ll))}')
            print('\nPrimeros registros despues de ordenar:')
            print_first_n_from_list(ll, 10)
        elif opt == '4':
            # Ordenar por Country
            if ll is None:
                print('Primero cargue la base (opcion 9)')
                continue
            field = 'country'
            keyfn = lambda r: getattr(r, field, None)
            ll = merge_sort_linkedlist(ll, keyfn)
            last_sort_field = field
            tree_for_last_sort = AVLTree(keyfn=lambda r: getattr(r, field, None))
            for rec in ll:
                tree_for_last_sort.insert(rec)
            print(f'Ordenado por Country (merge sort). Total registros: {len(list(ll))}')
            print('\nPrimeros registros despues de ordenar:')
            print_first_n_from_list(ll, 10)
        elif opt == '5':
            if ll is None:
                print('Primero cargue la base (opcion 9)')
                continue
            s = input("Ingrese numero de registros o 'todos' para mostrarlos todos: ").strip().lower()
            if s == 'todos' or s == '' or s == 't':
                n = None
            else:
                try:
                    n = int(s)
                    if n <= 0:
                        n = None
                except Exception:
                    print('Entrada invalida, mostrando todos')
                    n = None
            print_first_n_from_list(ll, n)
        elif opt == '6':
            if ll is None:
                print('Primero cargue la base (opcion 9)')
                continue
            # Busquedas por campo o rango de fechas
            choice = input('Buscar por (1)first_name (2)last_name (3)company (4)country (5)rango_fechas: ').strip()
            if choice in ('1','2','3','4'):
                field_map = {'1':'first_name','2':'last_name','3':'company','4':'country'}
                field = field_map[choice]
                value = input(f'Valor para {field}: ').strip()
                # Preguntamos si queremos construir indice por este campo (solo si no existe)
                if field not in indices:
                    ans = input(f"Construir indice por '{field}' para acelerar busqueda? (s/n): ").strip().lower()
                    if ans == 's':
                        idx = AVLTree(keyfn=lambda r: getattr(r, field, None))
                        print('Construyendo indice, esto puede tardar unos segundos...')
                        for rec in ll:
                            idx.insert(rec)
                        indices[field] = idx
                        print('Indice construido.')
                # tiempo usando indice/árbol si existe o generico
                t0 = time.perf_counter()
                if field in indices:
                    results_tree = indices[field].find(value)
                else:
                    # si existe tree_for_last_sort y su key coincide con field, buscar ahi
                    if tree_for_last_sort and last_sort_field == field:
                        results_tree = tree_for_last_sort.find(value)
                    else:
                        # usar recorrido completo del árbol principal si existe
                        if tree is not None:
                            results_tree = list(tree.find_by_predicate(lambda r: str(getattr(r, field, '')).lower() == value.lower()))
                        else:
                            results_tree = search_by_field_in_list(ll, field, value)
                t1 = time.perf_counter()
                # tiempo usando pila/cola (hacemos busqueda lineal en la linked list)
                t2 = time.perf_counter()
                results_list = search_by_field_in_list(ll, field, value)
                t3 = time.perf_counter()
                print(f'Encontrados en arbol: {len(results_tree)} (tiempo {t1-t0:.6f}s)')
                for r in results_tree:
                    print(r)
                print(f'---')
                print(f'Encontrados en lista/pila/cola: {len(results_list)} (tiempo {t3-t2:.6f}s)')
                for r in results_list:
                    print(r)
            else:
                # rango de fechas
                fmt = '%Y-%m-%d'
                s1 = input('Fecha inicio (YYYY-MM-DD): ').strip()
                s2 = input('Fecha fin (YYYY-MM-DD): ').strip()
                from datetime import datetime
                try:
                    d1 = datetime.strptime(s1, fmt).date()
                    d2 = datetime.strptime(s2, fmt).date()
                except Exception:
                    print('Formato de fecha invalido')
                    continue
                t0 = time.perf_counter()
                res_tree = search_by_date_range(tree if tree is not None else ll, d1, d2)
                t1 = time.perf_counter()
                t2 = time.perf_counter()
                res_list = search_by_date_range(ll, d1, d2)
                t3 = time.perf_counter()
                print(f'Registros encontrados (arbol): {len(res_tree)} (tiempo {t1-t0:.6f}s)')
                for r in res_tree:
                    print(r)
                print(f'---')
                print(f'Registros encontrados (lista): {len(res_list)} (tiempo {t3-t2:.6f}s)')
                for r in res_list:
                    print(r)
        elif opt == '7':
            # Estadisticas basicas
            if ll is None:
                print('Primero cargue la base (opcion 9)')
                continue
            # construimos indice por country si no existe
            if 'country' not in indices:
                idx = AVLTree(keyfn=lambda r: getattr(r, 'country', None))
                for rec in ll:
                    idx.insert(rec)
                indices['country'] = idx
            country_idx = indices['country']
            # total de paises = numero de claves distintas
            total_countries = 0
            for _ in country_idx.items():
                total_countries += 1
            print(f'Total de paises: {total_countries}')
            # clientes por pais: creamos lista enlazada (country, count)
            class CountryCount:
                def __init__(self, country, count):
                    self.country = country
                    self.count = count
                def __str__(self):
                    return f'{self.country}: {self.count}'

            cc_list = LinkedList()
            for key, records in country_idx.items():
                cc_list.append(CountryCount(key, len(records)))
            # ordenamos por count desc usando merge_sort (keyfn devuelve -count para invertir)
            cc_sorted = merge_sort_linkedlist(cc_list, keyfn=lambda x: -x.count)
            choice = input('Cuantos paises mostrar? (n para todos): ').strip()
            if choice.lower() == 'n' or choice == '':
                to_show = None
            else:
                try:
                    to_show = int(choice)
                except Exception:
                    to_show = None
            i = 0
            for item in cc_sorted:
                if to_show is not None and i >= to_show:
                    break
                print(item)
                i += 1
            # fechas min/max
            if stats:
                print(f'Fecha mas antigua: {stats["min_date"]}')
                print(f'Fecha mas reciente: {stats["max_date"]}')
        elif opt == '8':
            # Mostrar arbol binario por niveles segun ultimo criterio de orden
            if tree_for_last_sort is None:
                print('No hay criterio de orden aplicado aun. Ordene por algun campo primero.')
                continue
            print('Arbol por niveles (key - #registros en la clave):')
            for key, records in tree_for_last_sort.level_order():
                print(f'{key} - {len(records)}')
        elif opt == '9':
            path = input('Ruta del CSV: ').strip()
            if not os.path.exists(path):
                print('Archivo no encontrado')
                continue
            tree, ll, stk, q, stats = load_csv(path)
            # reset indices porque la base cambio
            indices = {}
            last_sort_field = None
            tree_for_last_sort = None
            print(f'Cargados {stats["count"]} registros. Fecha min: {stats["min_date"]} max: {stats["max_date"]}')
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
