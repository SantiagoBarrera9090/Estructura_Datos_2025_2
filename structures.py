"""
Estructuras de datos: Node, LinkedList, Stack, Queue, AVLTree.

Implementación basada en nodos enlazados para las colecciones principales.
Las lecturas temporales (por ejemplo, las filas de csv.reader) se consideran
estructuras temporales fuera de las colecciones de núcleo.
"""

class Node:
    """Un nodo simple que puede contener cualquier información y conectarse con otros nodos."""

    def __init__(self, data=None):
        self.data = data  # aquí guardamos la información que queremos almacenar
        self.next = None  # este apunta al siguiente nodo en la cadena
        self.prev = None  # este apunta al nodo anterior, para poder ir hacia atrás


class LinkedList:
    """Lista doblemente enlazada ligera.
    Lista doblemente enlazada ligera.

    Usada para mantener el orden original del archivo y para aplicar
    algoritmos de ordenamiento implementados sobre listas enlazadas.
    """

    def __init__(self):
        self.head = None  # este será el primer elemento de nuestra lista
        self.tail = None  # este será el último elemento de nuestra lista
        self._size = 0  # llevamos la cuenta de cuántos elementos tenemos

    def append(self, data):
        node = Node(data)  # creamos un nuevo nodo con la información
        if not self.head:  # si la lista está vacía
            self.head = self.tail = node  # este nuevo nodo será el primero y el último
        else:  # si ya hay elementos en la lista
            self.tail.next = node  # el último actual apunta al nuevo
            node.prev = self.tail  # el nuevo apunta hacia atrás al último actual
            self.tail = node  # ahora el nuevo es el último
        self._size += 1  # aumentamos el contador de elementos

    def __iter__(self):
        cur = self.head  # empezamos desde el primer nodo
        while cur:  # mientras tengamos un nodo que revisar
            yield cur.data  # devolvemos la información de este nodo
            cur = cur.next  # pasamos al siguiente nodo

    def is_empty(self):
        return self.head is None  # si no hay primer elemento, la lista está vacía

    def size(self):
        return self._size  # devolvemos cuántos elementos tenemos guardados

    def clear(self):
        self.head = None  # borramos la referencia al primer elemento
        self.tail = None  # borramos la referencia al último elemento
        self._size = 0  # reiniciamos el contador a cero


class Stack:
    """Implementacion simple de pila (LIFO) usando LinkedList.
    Implementación simple de pila (LIFO) usando LinkedList.

    Implementación sencilla y explícita para uso en búsquedas comparativas.
    """

    def __init__(self):
        self._list = LinkedList()  # usamos una lista enlazada para implementar la pila

    def push(self, item):
        node = Node(item)  # creamos un nuevo nodo con el elemento
        if self._list.head is None:  # si la pila está vacía
            self._list.head = self._list.tail = node  # este será el único elemento
        else:  # si ya hay elementos en la pila
            node.next = self._list.head  # el nuevo nodo apunta al que era primero
            self._list.head.prev = node  # el viejo primero apunta hacia atrás al nuevo
            self._list.head = node  # ahora el nuevo nodo es el primero
        self._list._size += 1  # aumentamos el tamaño de la pila

    def pop(self):
        if self._list.head is None:  # si la pila está vacía
            return None  # no hay nada que sacar
        node = self._list.head  # tomamos el primer elemento (el último que se metió)
        self._list.head = node.next  # el segundo elemento ahora es el primero
        if self._list.head:  # si queda algún elemento
            self._list.head.prev = None  # desconectamos su referencia hacia atrás
        else:  # si era el último elemento
            self._list.tail = None  # ya no hay cola
        node.next = None  # desconectamos el nodo que sacamos
        self._list._size -= 1  # reducimos el tamaño
        return node.data  # devolvemos la información del elemento

    def is_empty(self):
        return self._list.head is None  # verdadero si no hay primer elemento


class Queue:
    """Cola FIFO usando LinkedList.
    
    Una cola funciona como en la vida real: el primero en llegar es el primero en salir.
    Los elementos entran por atrás (enqueue) y salen por adelante (dequeue).
    """

    def __init__(self):
        self._list = LinkedList()  # usamos una lista enlazada para implementar la cola

    def enqueue(self, item):
        self._list.append(item)  # agregamos el elemento al final (como en una fila real)

    def dequeue(self):
        if self._list.head is None:  # si la cola está vacía
            return None  # no hay nada que sacar
        node = self._list.head  # tomamos el primer elemento (el más antiguo)
        self._list.head = node.next  # el segundo elemento ahora es el primero
        if self._list.head:  # si queda algún elemento
            self._list.head.prev = None  # desconectamos su referencia hacia atrás
        else:  # si era el último elemento
            self._list.tail = None  # ya no hay cola
        node.next = None  # desconectamos el nodo que sacamos
        self._list._size -= 1  # reducimos el tamaño
        return node.data  # devolvemos la información del elemento

    def is_empty(self):
        return self._list.head is None  # verdadero si no hay primer elemento


class AVLNode:
    def __init__(self, key, record):
        self.key = key  # la clave por la que vamos a ordenar este nodo
        # guardamos los registros en una LinkedList para soportar claves duplicadas
        self.records = LinkedList()  # lista de todos los registros con esta clave
        self.records.append(record)  # agregamos el primer registro
        self.left = None  # hijo izquierdo (claves menores)
        self.right = None  # hijo derecho (claves mayores)
        self.height = 1  # altura de este nodo en el árbol


class AVLTree:
    """Arbol AVL simple para almacenar (key, record).

    Comentario: el arbol esta pensado como indice principal; la key se obtiene
    por medio de la funcion keyfn que se pasa al constructor.
    """

    def __init__(self, keyfn=None):
        self.root = None  # la raíz es el nodo principal del árbol
        # función para obtener la clave desde un record
        self.keyfn = keyfn if keyfn else (lambda r: r.customer_id)  # cómo sacar la clave de cada registro
        self._count = 0  # llevamos la cuenta de cuántos registros hemos guardado

    def height(self, node):
        return node.height if node else 0  # si no hay nodo, la altura es cero

    def update_height(self, node):
        node.height = 1 + max(self.height(node.left), self.height(node.right))  # altura = 1 + la mayor altura de los hijos

    def balance_factor(self, node):
        return self.height(node.left) - self.height(node.right)  # diferencia de alturas para saber si está balanceado

    def rotate_right(self, y):
        x = y.left  # el hijo izquierdo será la nueva raíz
        T2 = x.right  # guardamos el subárbol derecho del nuevo raíz
        x.right = y  # el viejo raíz ahora es hijo derecho
        y.left = T2  # conectamos el subárbol que guardamos
        self.update_height(y)  # actualizamos la altura del viejo raíz
        self.update_height(x)  # actualizamos la altura del nuevo raíz
        return x  # devolvemos el nuevo raíz

    def rotate_left(self, x):
        y = x.right  # el hijo derecho será la nueva raíz
        T2 = y.left  # guardamos el subárbol izquierdo del nuevo raíz
        y.left = x  # el viejo raíz ahora es hijo izquierdo
        x.right = T2  # conectamos el subárbol que guardamos
        self.update_height(x)  # actualizamos la altura del viejo raíz
        self.update_height(y)  # actualizamos la altura del nuevo raíz
        return y  # devolvemos el nuevo raíz

    def _insert(self, node, key, record):
        if node is None:  # si llegamos a un lugar vacío
            return AVLNode(key, record)  # creamos un nuevo nodo aquí
        if key < node.key:  # si la clave es menor
            node.left = self._insert(node.left, key, record)  # insertamos a la izquierda
        elif key > node.key:  # si la clave es mayor
            node.right = self._insert(node.right, key, record)  # insertamos a la derecha
        else:  # si la clave es igual
            # clave igual: almacenamos el registro en la lista del nodo
            node.records.append(record)  # agregamos el registro a la lista existente
            return node  # no necesitamos balancear porque no cambió la estructura
        self.update_height(node)  # recalculamos la altura de este nodo
        bf = self.balance_factor(node)  # calculamos el factor de balance
        # casos de rotación para mantener el árbol balanceado
        if bf > 1 and key < node.left.key:  # caso izquierda-izquierda
            return self.rotate_right(node)  # rotación simple a la derecha
        if bf < -1 and key > node.right.key:  # caso derecha-derecha
            return self.rotate_left(node)  # rotación simple a la izquierda
        if bf > 1 and key > node.left.key:  # caso izquierda-derecha
            node.left = self.rotate_left(node.left)  # primero rotamos el hijo
            return self.rotate_right(node)  # luego rotamos este nodo
        if bf < -1 and key < node.right.key:  # caso derecha-izquierda
            node.right = self.rotate_right(node.right)  # primero rotamos el hijo
            return self.rotate_left(node)  # luego rotamos este nodo
        return node  # si no necesita rotación, devolvemos el nodo como está

    def insert(self, record):
        key = self.keyfn(record)  # extraemos la clave del registro usando nuestra función
        # insertamos y contamos
        self.root = self._insert(self.root, key, record)  # insertamos en el árbol y actualizamos la raíz
        self._count += 1  # aumentamos el contador de registros

    def find(self, key):
        """Busca por clave exacta y devuelve la lista de registros (o lista vacía)."""
        node = self.root  # empezamos desde la raíz del árbol
        while node:  # mientras tengamos un nodo que revisar
            if key == node.key:  # si encontramos la clave que buscamos
                # devolver una copia como LinkedList para evitar exponer la estructura interna
                out = LinkedList()  # creamos una nueva lista para los resultados
                for r in node.records:  # por cada registro en este nodo
                    out.append(r)  # lo agregamos a nuestra lista de resultados
                return out  # devolvemos todos los registros con esta clave
            elif key < node.key:  # si la clave buscada es menor
                node = node.left  # vamos hacia la izquierda
            else:  # si la clave buscada es mayor
                node = node.right  # vamos hacia la derecha
        return LinkedList()  # si no encontramos nada, devolvemos lista vacía

    def inorder(self):
        """Generador que recorre el árbol en orden (izquierda, raíz, derecha).
        
        Esto devuelve todos los registros ordenados por su clave.
        """
        # función interna para recorrer recursivamente
        def _in(node):
            if not node:  # si llegamos a un nodo vacío
                return  # no hay nada que procesar aquí
            yield from _in(node.left)  # primero procesamos todo el subárbol izquierdo
            # devolvemos cada registro del nodo (soporta duplicados)
            for rec in node.records:  # por cada registro guardado en este nodo
                yield rec  # lo devolvemos al que nos llamó
            yield from _in(node.right)  # finalmente procesamos todo el subárbol derecho

        yield from _in(self.root)  # empezamos el recorrido desde la raíz

    def items(self):
        """Generator que devuelve tuplas (key, records_list) por cada nodo en in-order.
        
        Útil cuando necesitas tanto la clave como todos los registros agrupados.
        """
        def _in(node):  # función interna para recorrer recursivamente
            if not node:  # si llegamos a un nodo vacío
                return  # no hay nada que procesar aquí
            yield from _in(node.left)  # primero procesamos todo el subárbol izquierdo
            # devolvemos la LinkedList interna (no la convertimos a list)
            yield (node.key, node.records)  # devolvemos la clave y su lista de registros
            yield from _in(node.right)  # finalmente procesamos todo el subárbol derecho

        yield from _in(self.root)  # empezamos el recorrido desde la raíz

    def level_order(self):
        """Generator por niveles que devuelve (key, records_list) para visualizacion.
        
        Recorre el árbol nivel por nivel, de izquierda a derecha.
        """
        if not self.root:  # si el árbol está vacío
            return  # no hay nada que mostrar
        # usar la Queue propia para evitar listas Python en estructuras núcleo
        q = Queue()  # creamos una cola para procesar nodos nivel por nivel
        q.enqueue(self.root)  # metemos la raíz como primer elemento
        while not q.is_empty():  # mientras tengamos nodos por procesar
            node = q.dequeue()  # sacamos el siguiente nodo de la cola
            yield (node.key, node.records)  # devolvemos la clave y todos sus registros
            if node.left:  # si este nodo tiene hijo izquierdo
                q.enqueue(node.left)  # lo metemos a la cola para procesarlo después
            if node.right:  # si este nodo tiene hijo derecho
                q.enqueue(node.right)  # lo metemos a la cola para procesarlo después

    def size(self):
        return self._count  # devolvemos cuántos registros hemos guardado en total

    def find_by_predicate(self, predicate):
        """Recorre el árbol y devuelve registros que cumplen predicate(record).

        Se usa yield para no almacenar todo en memoria.
        """

        def _in(node):  # función interna para recorrer el árbol
            if not node:  # si llegamos a un nodo vacío
                return  # no hay nada que hacer aquí
            yield from _in(node.left)  # primero revisamos todos los hijos izquierdos
            # aplicamos predicate a cada registro almacenado en el nodo
            for rec in node.records:  # por cada registro en este nodo
                try:
                    if predicate(rec):  # si el registro cumple la condición
                        yield rec  # lo devolvemos
                except Exception:
                    # si la predicate falla para un registro, la ignoramos
                    continue  # seguimos con el siguiente registro
            yield from _in(node.right)  # después revisamos todos los hijos derechos

        yield from _in(self.root)  # empezamos el recorrido desde la raíz


