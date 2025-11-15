"""
Estructuras de datos: Node, LinkedList, Stack, Queue, AVLTree.

Implementación basada en nodos enlazados para las colecciones principales.
Las lecturas temporales (por ejemplo, las filas de csv.reader) se consideran
estructuras temporales fuera de las colecciones de núcleo.
"""

class Node:
    """Nodo basico para listas enlazadas."""

    def __init__(self, data=None):
        self.data = data
        self.next = None
        self.prev = None


class LinkedList:
    """Lista doblemente enlazada ligera.
    Lista doblemente enlazada ligera.

    Usada para mantener el orden original del archivo y para aplicar
    algoritmos de ordenamiento implementados sobre listas enlazadas.
    """

    def __init__(self):
        self.head = None
        self.tail = None
        self._size = 0

    def append(self, data):
        node = Node(data)
        if not self.head:
            self.head = self.tail = node
        else:
            self.tail.next = node
            node.prev = self.tail
            self.tail = node
        self._size += 1

    def __iter__(self):
        cur = self.head
        while cur:
            yield cur.data
            cur = cur.next

    def is_empty(self):
        return self.head is None

    def size(self):
        return self._size

    def clear(self):
        self.head = None
        self.tail = None
        self._size = 0


class Stack:
    """Implementacion simple de pila (LIFO) usando LinkedList.
    Implementación simple de pila (LIFO) usando LinkedList.

    Implementación sencilla y explícita para uso en búsquedas comparativas.
    """

    def __init__(self):
        self._list = LinkedList()

    def push(self, item):
        node = Node(item)
        if self._list.head is None:
            self._list.head = self._list.tail = node
        else:
            node.next = self._list.head
            self._list.head.prev = node
            self._list.head = node
        self._list._size += 1

    def pop(self):
        if self._list.head is None:
            return None
        node = self._list.head
        self._list.head = node.next
        if self._list.head:
            self._list.head.prev = None
        else:
            self._list.tail = None
        node.next = None
        self._list._size -= 1
        return node.data

    def is_empty(self):
        return self._list.head is None


class Queue:
    """Cola FIFO usando LinkedList."""

    def __init__(self):
        self._list = LinkedList()

    def enqueue(self, item):
        self._list.append(item)

    def dequeue(self):
        if self._list.head is None:
            return None
        node = self._list.head
        self._list.head = node.next
        if self._list.head:
            self._list.head.prev = None
        else:
            self._list.tail = None
        node.next = None
        self._list._size -= 1
        return node.data

    def is_empty(self):
        return self._list.head is None


class AVLNode:
    def __init__(self, key, record):
        self.key = key
        # guardamos los registros en una LinkedList para soportar claves duplicadas
        self.records = LinkedList()
        self.records.append(record)
        self.left = None
        self.right = None
        self.height = 1


class AVLTree:
    """Arbol AVL simple para almacenar (key, record).

    Comentario: el arbol esta pensado como indice principal; la key se obtiene
    por medio de la funcion keyfn que se pasa al constructor.
    """

    def __init__(self, keyfn=None):
        self.root = None
        # función para obtener la clave desde un record
        self.keyfn = keyfn if keyfn else (lambda r: r.customer_id)
        self._count = 0

    def height(self, node):
        return node.height if node else 0

    def update_height(self, node):
        node.height = 1 + max(self.height(node.left), self.height(node.right))

    def balance_factor(self, node):
        return self.height(node.left) - self.height(node.right)

    def rotate_right(self, y):
        x = y.left
        T2 = x.right
        x.right = y
        y.left = T2
        self.update_height(y)
        self.update_height(x)
        return x

    def rotate_left(self, x):
        y = x.right
        T2 = y.left
        y.left = x
        x.right = T2
        self.update_height(x)
        self.update_height(y)
        return y

    def _insert(self, node, key, record):
        if node is None:
            return AVLNode(key, record)
        if key < node.key:
            node.left = self._insert(node.left, key, record)
        elif key > node.key:
            node.right = self._insert(node.right, key, record)
        else:
            # clave igual: almacenamos el registro en la lista del nodo
            node.records.append(record)
            return node
        self.update_height(node)
        bf = self.balance_factor(node)
        # casos de rotación
        if bf > 1 and key < node.left.key:
            return self.rotate_right(node)
        if bf < -1 and key > node.right.key:
            return self.rotate_left(node)
        if bf > 1 and key > node.left.key:
            node.left = self.rotate_left(node.left)
            return self.rotate_right(node)
        if bf < -1 and key < node.right.key:
            node.right = self.rotate_right(node.right)
            return self.rotate_left(node)
        return node

    def insert(self, record):
        key = self.keyfn(record)
        # insertamos y contamos
        self.root = self._insert(self.root, key, record)
        self._count += 1

    def find(self, key):
        """Busca por clave exacta y devuelve la lista de registros (o lista vacía)."""
        node = self.root
        while node:
            if key == node.key:
                # devolver una copia como LinkedList para evitar exponer la estructura interna
                out = LinkedList()
                for r in node.records:
                    out.append(r)
                return out
            elif key < node.key:
                node = node.left
            else:
                node = node.right
        return LinkedList()

    def inorder(self):
        # generator in-order
        def _in(node):
            if not node:
                return
            yield from _in(node.left)
            # devolvemos cada registro del nodo (soporta duplicados)
            for rec in node.records:
                yield rec
            yield from _in(node.right)

        yield from _in(self.root)

    def items(self):
        """Generator que devuelve tuplas (key, records_list) por cada nodo en in-order."""
        def _in(node):
            if not node:
                return
            yield from _in(node.left)
            # devolvemos la LinkedList interna (no la convertimos a list)
            yield (node.key, node.records)
            yield from _in(node.right)

        yield from _in(self.root)

    def level_order(self):
        """Generator por niveles que devuelve (key, records_list) para visualizacion."""
        if not self.root:
            return
        # usar la Queue propia para evitar listas Python en estructuras núcleo
        q = Queue()
        q.enqueue(self.root)
        while not q.is_empty():
            node = q.dequeue()
            yield (node.key, node.records)
            if node.left:
                q.enqueue(node.left)
            if node.right:
                q.enqueue(node.right)

    def size(self):
        return self._count

    def find_by_predicate(self, predicate):
        """Recorre el árbol y devuelve registros que cumplen predicate(record).

        Se usa yield para no almacenar todo en memoria.
        """

        def _in(node):
            if not node:
                return
            yield from _in(node.left)
            # aplicamos predicate a cada registro almacenado en el nodo
            for rec in node.records:
                try:
                    if predicate(rec):
                        yield rec
                except Exception:
                    # si la predicate falla para un registro, la ignoramos
                    continue
            yield from _in(node.right)

        yield from _in(self.root)

    def level_order(self):
        # Recorrido por niveles del árbol binario
        # Retorna generator que itera (key, records) por niveles
        if not self.root:  # árbol vacío
            return
        
        # Usar Queue para recorrido por niveles
        q = Queue()  # cola de nodos por procesar
        q.enqueue(self.root)  # agregar raíz
        
        while not q.is_empty():  # mientras haya nodos
            node = q.dequeue()  # obtener siguiente nodo
            yield (node.key, node.records)  # devolver clave y registros
            
            if node.left:  # si tiene hijo izquierdo
                q.enqueue(node.left)  # agregar a cola
            if node.right:  # si tiene hijo derecho
                q.enqueue(node.right)  # agregar a cola
