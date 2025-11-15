#!/usr/bin/env python3
"""Test automatizado del sistema completo"""

import time
from structures import LinkedList, Stack, Queue, AVLTree
from models import Record
from main import load_csv
from datetime import datetime

def test_complete_system():
    print("=== Prueba automatizada del sistema ===")
    
    # 1. Cargar datos
    print("\n1. Cargando datos...")
    try:
        tree, ll, stk, q, stats = load_csv('BusinessData.csv')
        print(f"✓ Cargados {ll.size()} registros")
        print(f"✓ Fecha mínima: {stats['min_date']}")
        print(f"✓ Fecha máxima: {stats['max_date']}")
    except Exception as e:
        print(f"✗ Error cargando datos: {e}")
        return
    
    # 2. Probar ordenamiento
    print("\n2. Probando ordenamientos...")
    from sorting import merge_sort_linkedlist, quick_sort_linkedlist
    
    # Ordenar por customer_id (pocos registros para probar)
    small_ll = LinkedList()
    count = 0
    for rec in ll:
        small_ll.append(rec)
        count += 1
        if count >= 100:  # Solo 100 para prueba rápida
            break
    
    sorted_ll = merge_sort_linkedlist(small_ll, keyfn=lambda r: r.customer_id)
    print(f"✓ Ordenamiento por customer_id: {sorted_ll.size()} registros")
    
    # 3. Probar búsquedas
    print("\n3. Probando búsquedas...")
    from main import search_by_field_in_tree, search_by_field_in_stack
    
    # Crear árbol con pocos datos
    test_tree = AVLTree(keyfn=lambda r: r.country)
    for rec in small_ll:
        test_tree.insert(rec)
    
    # Buscar un país común
    test_stack = Stack()
    for rec in small_ll:
        test_stack.push(rec)
    
    # Probar búsqueda por país
    t0 = time.perf_counter()
    results_tree = search_by_field_in_tree(test_tree, 'country', 'United States')
    t1 = time.perf_counter()
    
    t2 = time.perf_counter()
    results_stack = search_by_field_in_stack(test_stack, 'country', 'United States')
    t3 = time.perf_counter()
    
    print(f"✓ Búsqueda en árbol: {results_tree.size()} resultados ({t1-t0:.6f}s)")
    print(f"✓ Búsqueda en pila: {results_stack.size()} resultados ({t3-t2:.6f}s)")
    
    # 4. Probar visualización por niveles
    print("\n4. Probando visualización por niveles...")
    level_count = 0
    for key, records in test_tree.level_order():
        if level_count < 5:  # Solo mostrar primeros 5 niveles
            print(f"  Nivel: {key} -> {records.size()} registros")
            level_count += 1
        else:
            break
    print("✓ Visualización por niveles funciona")
    
    # 5. Probar estadísticas
    print("\n5. Probando estadísticas...")
    # Contar países únicos
    countries = set()
    for rec in small_ll:
        if rec.country:
            countries.add(rec.country)
    print(f"✓ Países únicos en muestra: {len(countries)}")
    
    print("\n=== Todas las pruebas completadas exitosamente ===")

if __name__ == "__main__":
    test_complete_system()