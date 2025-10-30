"""Algoritmos de ordenamiento manuales para listas enlazadas: MergeSort y QuickSort.

Comentarios: aqui implemento versiones que funcionan con la LinkedList propia.
El estilo de los comentarios es ameno, como si fuera un estudiante colombiano
explicando lo que hace el codigo.
"""

from structures import LinkedList


def _normalize_key(keyfn, record):
    """Normaliza la clave para comparaciones seguras.

    Devuelve una tupla (type_tag, value) donde type_tag ordena tipos:
    - 0: valores ordenables directos (int, float, date, datetime)
    - 1: strings (se comparan en minuscula)
    - 2: fallback (cadena vacia)

    Esto evita comparar tipos incompatibles directamente.
    """
    try:
        v = keyfn(record)
    except Exception:
        return (2, "")
    if v is None:
        return (2, "")
    # import aquí para evitar dependencia global
    from datetime import date, datetime

    if isinstance(v, (int, float)):
        return (0, v)
    if isinstance(v, (date, datetime)):
        return (0, v)
    # booleanes se tratan como ints
    if isinstance(v, bool):
        return (0, int(v))
    # por defecto, tratamos como string
    try:
        s = str(v).lower()
        return (1, s)
    except Exception:
        return (2, "")


def split_linkedlist(ll: LinkedList):
    """Divide una linked list en dos mitades y devuelve (left, right).

    Ojo: esto no modifica los datos, solo separa las referencias para trabajar
    con ellas luego en el merge sort.
    """
    if ll.head is None or ll.head.next is None:
        left = LinkedList()
        cur = ll.head
        while cur:
            left.append(cur.data)
            cur = cur.next
        right = LinkedList()
        return left, right

    slow = ll.head
    fast = ll.head
    while fast.next and fast.next.next:
        slow = slow.next
        fast = fast.next.next

    # slow queda al final de la primera mitad
    left = LinkedList()
    cur = ll.head
    while cur is not None and cur is not slow.next:
        left.append(cur.data)
        cur = cur.next

    right = LinkedList()
    cur = slow.next
    while cur:
        right.append(cur.data)
        cur = cur.next

    return left, right


def merge_sorted(left: LinkedList, right: LinkedList, keyfn):
    """Fusiona dos listas ya ordenadas segun keyfn."""
    result = LinkedList()
    a = left.head
    b = right.head
    while a and b:
        if _normalize_key(keyfn, a.data) <= _normalize_key(keyfn, b.data):
            result.append(a.data)
            a = a.next
        else:
            result.append(b.data)
            b = b.next
    while a:
        result.append(a.data)
        a = a.next
    while b:
        result.append(b.data)
        b = b.next
    return result


def merge_sort_linkedlist(ll: LinkedList, keyfn=lambda r: r.customer_id):
    """Merge sort recursivo para linked lists.

    Retorna una nueva LinkedList ordenada.
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

    Es recursivo y sencillo; no es la version mas rapida pero cumple el objetivo.
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
