# Sistema de Gestión de Clientes - Implementación Completa

## Descripción General

Sistema desarrollado en Python que permite cargar, ordenar y consultar eficientemente un archivo de datos con más de 100,000 registros utilizando estructuras de datos implementadas manualmente.

## Características Técnicas

### Estructuras de Datos Implementadas

- **LinkedList**: Lista doblemente enlazada con métodos append, prepend, remove, size, e iteración
- **Stack**: Pila LIFO (Last In, First Out) con operaciones push, pop, is_empty
- **Queue**: Cola FIFO (First In, First Out) con operaciones enqueue, dequeue, is_empty
- **AVLTree**: Árbol binario autobalanceado con operaciones insert, búsqueda por predicado, recorrido por niveles

### Algoritmos de Ordenamiento

- **MergeSort**: Implementado para LinkedList con complejidad O(n log n)
- **QuickSort**: Implementado para LinkedList con complejidad promedio O(n log n)
- Ambos algoritmos utilizan funciones de clave personalizables para diferentes campos

### Modelo de Datos

La clase `Record` representa cada registro de cliente con los siguientes campos:

- customer_id: Identificador único del cliente
- first_name: Nombre del cliente
- last_name: Apellido del cliente
- company: Empresa del cliente
- city: Ciudad del cliente
- country: País del cliente
- email: Correo electrónico
- subscription_date: Fecha de suscripción (tipo date)
- website: Sitio web del cliente

## Funcionalidades del Menú

### 0. Salir

Termina la ejecución del programa.

### 1. Ordenar por Customer ID

- Utiliza MergeSort para ordenar por identificador de cliente
- Crea un índice AVLTree para búsquedas eficientes
- Muestra los primeros 10 registros como preview

### 2. Ordenar por First Name

- Utiliza MergeSort para ordenar alfabéticamente por nombre
- Crea un índice AVLTree correspondiente
- Muestra preview de resultados

### 3. Ordenar por Subscription Date

- Utiliza QuickSort para ordenar cronológicamente por fecha de suscripción
- Maneja fechas nulas colocándolas al final
- Crea índice temporal para visualización

### 4. Ordenar por Country

- Utiliza MergeSort para ordenar alfabéticamente por país
- Agrupa clientes del mismo país
- Construye índice para operaciones posteriores

### 5. Mostrar Registros

- Permite mostrar un número específico de registros o todos
- Utiliza la última ordenación aplicada
- Formato de salida: todos los campos separados por " - "

### 6. Búsquedas Avanzadas ⭐ NUEVO

Permite búsquedas por:

- **First Name**: Búsqueda exacta case-insensitive
- **Last Name**: Búsqueda exacta case-insensitive
- **Company**: Búsqueda exacta case-insensitive
- **Country**: Búsqueda exacta case-insensitive
- **Rango de Fechas**: Búsqueda por rango de fechas de suscripción (formato YYYY-MM-DD)

**Comparación de Rendimiento**: Para cada búsqueda se miden y comparan los tiempos de:

- Búsqueda en AVLTree (más eficiente - O(log n))
- Búsqueda en Stack (menos eficiente - O(n))
- Búsqueda en Queue (menos eficiente - O(n))

### 7. Estadísticas Básicas ⭐ NUEVO

- **Total de países únicos**: Cuenta países distintos en la base de datos
- **Clientes por país**: Lista ordenada descendente por número de clientes
- **Fechas extremas**: Muestra fecha de suscripción más antigua y más reciente
- Permite mostrar todos los países o un número específico

### 8. Visualización de Árbol Binario ⭐ NUEVO

- Muestra el árbol binario por niveles basado en el último ordenamiento aplicado
- Recorrido nivel por nivel (breadth-first traversal)
- Formato: `clave - número_de_registros`
- Requiere haber aplicado un ordenamiento previo (opciones 1-4)

## Requisitos Técnicos Cumplidos

### ✅ Implementación Manual

- **NO** se utilizan las estructuras predefinidas de Python (list, dict, set)
- **NO** se usa list.sort() ni métodos de ordenamiento integrados
- **NO** se importan librerías externas (solo csv, time, datetime del standard library)
- Todas las estructuras están implementadas desde cero con nodos enlazados

### ✅ Manejo de Datos Masivos

- Carga eficiente de 100,000+ registros
- Estructuras optimizadas para memoria
- Algoritmos con complejidad temporal eficiente

### ✅ Medición de Rendimiento

- Comparación de tiempos entre AVLTree y estructuras lineales
- Medición precisa con time.perf_counter()
- Demostración clara de ventajas del árbol binario

### ✅ Robustez

- Manejo de errores en parsing de fechas
- Validación de entrada de usuario
- Recuperación de estado de estructuras después de búsquedas destructivas

## Archivos del Proyecto

- `main.py`: Punto de entrada, menú interactivo, carga de CSV
- `structures.py`: Implementación de todas las estructuras de datos
- `sorting.py`: Algoritmos de ordenamiento MergeSort y QuickSort
- `models.py`: Definición de la clase Record
- `test_system.py`: Pruebas automatizadas del sistema
- `BusinessData.csv`: Archivo de datos con 100,000 registros
- `.gitignore`: Configuración para ignorar archivos temporales

## Complejidades Computacionales

| Operación             | AVLTree  | LinkedList | Stack/Queue |
| --------------------- | -------- | ---------- | ----------- |
| Inserción             | O(log n) | O(1)       | O(1)        |
| Búsqueda              | O(log n) | O(n)       | O(n)        |
| Ordenamiento          | -        | O(n log n) | -           |
| Recorrido por niveles | O(n)     | -          | -           |

## Características Especiales ⭐

### ✅ Sin Limitaciones de Visualización

- **Muestra TODA la información** sin restricciones
- **No hay límites** en número de registros mostrados
- **Información completa** en todas las operaciones
- **Datos exhaustivos** en búsquedas y estadísticas

### ✅ Comentarios Naturales

- Comentarios escritos en **lenguaje natural y comprensible**
- Explicaciones **línea por línea** de cada operación
- Documentación **fácil de entender** sin tecnicismos excesivos
- Código **autodocumentado** para facilitar el aprendizaje

## Ejecución

```bash
python main.py
```

El sistema detectará automáticamente el archivo `BusinessData.csv` y ofrecerá cargarlo. Una vez cargado, todas las opciones del menú 0-8 estarán completamente funcionales **mostrando toda la información sin limitaciones**.

## Pruebas

```bash
python test_system.py
```

Ejecuta una suite de pruebas automatizadas que verifican:

- Carga correcta de datos
- Funcionamiento de algoritmos de ordenamiento
- Búsquedas y comparación de tiempos
- Visualización por niveles
- Cálculo de estadísticas

---

**Desarrollo**: Sistema implementado siguiendo estrictamente los requisitos de implementación manual de estructuras de datos, sin uso de librerías externas ni funciones predefinidas de Python para las operaciones core del sistema.
