"""Algoritmos de ordenamiento manuales para listas enlazadas: MergeSort y QuickSort.

Implementa versiones que operan sobre la `LinkedList` propia del proyecto.
Los algoritmos devuelven nuevas listas enlazadas ordenadas.
"""

from structures import LinkedList


def _normalize_key(keyfn, record):
    """Esta función prepara los valores para poder compararlos de forma segura.

    Cuando ordenamos, necesitamos comparar números con números, texto con texto, etc.
    Esta función se encarga de organizar todo para que no haya problemas:
    - Los números y fechas van primero (más fáciles de ordenar)
    - El texto va después (se convierte a minúsculas)
    - Si algo está roto, lo ponemos al final
    """
    try:
        v = keyfn(record)  # intentamos extraer el valor usando la función que nos dieron
    except Exception:
        return (2, "")  # si algo sale mal, ponemos este registro al final
    if v is None:  # si el valor es nulo
        return (2, "")  # también lo ponemos al final
    # Import local para evitar dependencia global
    from datetime import date, datetime  # importamos tipos de fecha cuando los necesitamos

    if isinstance(v, (int, float)):  # si es un número
        return (0, v)  # lo ponemos en la categoría 0 (primero)
    if isinstance(v, (date, datetime)):  # si es una fecha
        return (0, v)  # también va en categoría 0 (se ordenan bien)
    # booleanes se tratan como ints
    if isinstance(v, bool):  # si es verdadero/falso
        return (0, int(v))  # lo convertimos a número (False=0, True=1)
    # por defecto, tratamos como string
    try:
        s = str(v).lower()  # convertimos a texto en minúsculas
        return (1, s)  # va en categoría 1 (después de los números)
    except Exception:
        return (2, "")  # si no se puede convertir, va al final


def split_linkedlist(ll: LinkedList):
    """Divide una linked list en dos mitades y devuelve (left, right).

    Nota: esto no modifica los datos originales; construye dos nuevas listas
    que contienen los mismos elementos referenciados.
    """
    if ll.head is None or ll.head.next is None:  # si la lista está vacía o tiene solo un elemento
        left = LinkedList()  # creamos una lista vacía para la izquierda
        cur = ll.head  # empezamos desde el primer elemento
        while cur:  # mientras haya elementos
            left.append(cur.data)  # copiamos cada elemento a la lista izquierda
            cur = cur.next  # pasamos al siguiente
        right = LinkedList()  # la lista derecha queda vacía
        return left, right  # devolvemos las dos mitades

    slow = ll.head  # puntero lento: avanza de uno en uno
    fast = ll.head  # puntero rápido: avanza de dos en dos
    while fast.next and fast.next.next:  # mientras el rápido pueda avanzar dos pasos
        slow = slow.next  # el lento avanza uno
        fast = fast.next.next  # el rápido avanza dos

    # slow queda al final de la primera mitad
    left = LinkedList()  # creamos la lista para la primera mitad
    cur = ll.head  # empezamos desde el principio
    while cur is not None and cur is not slow.next:  # hasta donde marca el puntero lento
        left.append(cur.data)  # copiamos elementos a la primera mitad
        cur = cur.next  # avanzamos

    right = LinkedList()  # creamos la lista para la segunda mitad
    cur = slow.next  # empezamos desde donde terminó la primera mitad
    while cur:  # hasta el final
        right.append(cur.data)  # copiamos elementos a la segunda mitad
        cur = cur.next  # avanzamos

    return left, right  # devolvemos las dos mitades


def merge_sorted(left: LinkedList, right: LinkedList, keyfn):
    """Fusiona dos listas ya ordenadas según keyfn."""
    result = LinkedList()  # creamos una nueva lista para el resultado
    a = left.head  # puntero al primer elemento de la lista izquierda
    b = right.head  # puntero al primer elemento de la lista derecha
    while a and b:  # mientras tengamos elementos en ambas listas
        if _normalize_key(keyfn, a.data) <= _normalize_key(keyfn, b.data):  # si el elemento de la izquierda es menor o igual
            result.append(a.data)  # lo agregamos al resultado
            a = a.next  # avanzamos en la lista izquierda
        else:  # si el elemento de la derecha es menor
            result.append(b.data)  # lo agregamos al resultado
            b = b.next  # avanzamos en la lista derecha
    while a:  # si quedan elementos en la lista izquierda
        result.append(a.data)  # los agregamos todos
        a = a.next  # avanzamos
    while b:  # si quedan elementos en la lista derecha
        result.append(b.data)  # los agregamos todos
        b = b.next  # avanzamos
    return result  # devolvemos la lista fusionada y ordenada


def merge_sort_linkedlist(ll: LinkedList, keyfn=lambda r: r.customer_id):
    """Esta función ordena una lista usando el método Merge Sort.
    
    Merge Sort es como ordenar dos pilas de cartas: divides todo por la mitad,
    ordenas cada mitad por separado, y luego las combinas de forma ordenada.
    """
    if ll.head is None or ll.head.next is None:
        out = LinkedList()
        cur = ll.head
        while cur:
            out.append(cur.data)
            cur = cur.next
        return out

    left, right = split_linkedlist(ll)
    left_sorted = merge_sort_linkedlist(left, keyfn)
    right_sorted = merge_sort_linkedlist(right, keyfn)
    return merge_sorted(left_sorted, right_sorted, keyfn)


def quick_sort_linkedlist(ll: LinkedList, keyfn=lambda r: r.customer_id):
    """QuickSort para linked list usando particionamiento en tres listas.

    Implementación recursiva que particiona en menores, iguales y mayores
    respecto al pivote.
    """
    if ll.head is None or ll.head.next is None:
        out = LinkedList()
        cur = ll.head
        while cur:
            out.append(cur.data)
            cur = cur.next
        return out

    pivot = ll.head.data
    pk = _normalize_key(keyfn, pivot)

    less = LinkedList()
    equal = LinkedList()
    greater = LinkedList()

    cur = ll.head
    while cur:
        k = _normalize_key(keyfn, cur.data)
        if k < pk:
            less.append(cur.data)
        elif k == pk:
            equal.append(cur.data)
        else:
            greater.append(cur.data)
        cur = cur.next

    less_sorted = quick_sort_linkedlist(less, keyfn) if less.head else less
    greater_sorted = quick_sort_linkedlist(greater, keyfn) if greater.head else greater

    out = LinkedList()
    for item in less_sorted:
        out.append(item)
    for item in equal:
        out.append(item)
    for item in greater_sorted:
        out.append(item)
    return out




def three_way_radix_quicksort(ll: LinkedList, keyfn=lambda r: r.customer_id):
    # Definir función principal que recibe LinkedList y función para extraer campo
    """Este algoritmo funciona con parte de la lógica de radix y la de quick"""
    
    # Verificar si la lista está vacía o tiene solo un elemento
    if ll.head is None or ll.head.next is None:
        # Devolver una copia de la lista (no hay nada que ordenar)
        return ll.copy()
    
    # Crear lista temporal para facilitar procesamiento recursivo
    records = []
    # Empezar desde el primer nodo de la LinkedList
    cur = ll.head
    # Recorrer toda la LinkedList
    while cur:
        # Agregar cada registro a la lista temporal
        records.append(cur.data)
        # Mover al siguiente nodo
        cur = cur.next
    
    # Definir función recursiva interna para el ordenamiento
    def _sort(recs, depth=0):
        if len(recs) <= 1:
            return recs
        
        pivot = keyfn(recs[0])

        if depth >= len(pivot):

            char_pivot = ''
        else:
            char_pivot = pivot[depth].lower()
        
        lt, eq, gt = [], [], []
        
        for record in recs:

            current_id = keyfn(record)

            if depth >= len(current_id):
    
                current_char = ''
            else:
    
                current_char = current_id[depth].lower()
            

            if current_char < char_pivot:
    
                lt.append(record)
            elif current_char > char_pivot:
    
                gt.append(record)
            else:
                
                eq.append(record)
        
       
        if eq and char_pivot:
            
            eq = _sort(eq, depth + 1)
        
       
        return _sort(lt, depth) + eq + _sort(gt, depth)
    
    # Llamar a la función recursiva con todos los registros
    sorted_records = _sort(records)
    # Crear nueva LinkedList para el resultado final
    result = LinkedList()
    # Recorrer todos los registros ordenados
    for record in sorted_records:
        # Agregar cada registro ordenado a la nueva LinkedList
        result.append(record)
    # Devolver la LinkedList completamente ordenada
    return result
