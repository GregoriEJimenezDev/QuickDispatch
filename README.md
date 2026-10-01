# QuickDispatch

App de consola en Python para gestión logística de pedidos e incidencias.
Pedidos pendientes en cola FIFO y devoluciones/cancelaciones en pila LIFO,
ambas con lista enlazada simple. Históricos en diccionarios nativos.

## Cómo ejecutar

```bash
cd QuickDispatch
python main.py
```

Requiere Python 3.10 o superior (se usa `X | None` en anotaciones).

La cantidad de cajas se pide como entero mayor que 0 y admite **hasta 9 dígitos**;
si el texto no es numérico, es cero o supera ese tope, la interfaz vuelve a
pedirlo con un mensaje propio para cada caso.

La interfaz usa una columna centrada de 100 caracteres (se adapta al ancho de la
terminal con un mínimo de 40); conviene maximizar o ajustar la ventana antes de ejecutar.

## Pruebas

```bash
cd QuickDispatch
python -m unittest discover -v
```

`tests/` contiene pruebas automáticas con `unittest` (biblioteca estándar, sin
dependencias): cola FIFO y pila LIFO, registro y despacho de pedidos, registro y
procesamiento de incidencias, y flujos completos de la interfaz por stdin
(salida limpia, EOF, mensajes de validación y despacho en orden FIFO).

## Estructura de carpetas

- `main.py`: composición de dependencias (`build_app`) y entrada (`main`).
- `models/`: entidades `Order` e `Incident`, enums (`enums.py`), nodo `Node`.
- `models/operation_result.py`: retorno único `OperationResult` de cada operación.
- `data_structures/`: cola FIFO (`front`/`rear`) y pila LIFO (`top`) con lista enlazada.
- `orders/` e `incidents/`: factories, builders y servicios de cada flujo.
- `validators/`: reglas de validación inyectables.
- `ui/`: utilidades de consola y menú principal de 6 opciones.
- `tests/`: pruebas automáticas con `unittest` (cola, pila, pedidos, incidencias y CLI).
- `requirements.txt`: nota de versión mínima de Python (sin dependencias).

## Complejidades por operación

Cola FIFO (`QueueLinkedList`):

| Operación | Complejidad | Por qué |
| --- | --- | --- |
| `enqueue(dato)` | O(1) | enlaza el nodo nuevo en `rear` y fija `front` si estaba vacía |
| `dequeue()` | O(1) | extrae el nodo de `front` y avanza la referencia |
| `peek()` | O(1) | lee `front` sin extraer |
| `is_empty()` / `len()` | O(1) | contador incremental `_size` |
| `traverse_forward()` | O(n) | recorre los n nodos desde `front`, sin copiarlos |

Pila LIFO (`StackLinkedList`):

| Operación | Complejidad | Por qué |
| --- | --- | --- |
| `push(dato)` | O(1) | enlaza el nodo nuevo como `top` |
| `pop()` | O(1) | extrae el nodo de `top` y avanza la referencia |
| `peek()` | O(1) | lee `top` sin extraer |
| `is_empty()` / `len()` | O(1) | contador incremental `_size` |
| `traverse_from_top()` | O(n) | recorre los n nodos desde `top`, sin copiarlos |

Ninguna operación supera O(n) y ningún recorrido está anidado con otro.

## Justificación de estructuras de datos

**Queue (cola) para pedidos.** Se despacha por orden de llegada (FIFO): el
primero registrado es el primero despachado, que es la regla de negocio de
reparto. Con `front` y `rear`, `enqueue`, `dequeue` y `peek` son O(1) y no
dependen del tamaño de la cola.

**Stack (pila) para incidencias.** Se atiende primero la más reciente (LIFO):
el último reclamo es el más urgente y debe resolverse antes que los
anteriores. Con `top`, `push`, `pop` y `peek` son O(1) sin recorrer nodos.

**Por qué lista enlazada simple.** Insertar y extraer en cualquier extremo
cuesta O(1) con dos referencias (`front`/`rear`) o una (`top`): solo se
enlaza o desenlaza el nodo afectado y se actualiza el contador, sin
reasignar memoria de un bloque contiguo ni desplazar elementos como haría
una lista nativa al insertar al inicio. Los históricos de pedidos
despachados e incidencias procesadas usan acceso directo por clave en
diccionarios nativos.

## Factory y Builder

Viven en `orders/` (`OrderFactory`, `OrderBuilder`) e `incidents/`
(`IncidentFactory`, `IncidentBuilder`). Se reparten el trabajo: el Builder
recibe y normaliza la entrada (strip, mayúsculas, alias sin tilde) con setters
encadenables (`with_nombre`, `with_apellido`, `with_cajas`, `with_tipo`,
`with_order_id`, `with_motivo`); la Factory valida, emite el ID único
(`Order-0001`, `Incident-0001`), asigna fecha y estado, e instancia el modelo.
Los estados y tipos son enums (`OrderStatus`, `IncidentStatus`,
`IncidentType`) con los mismos textos de siempre.

## Convención de complejidad

Cada método y función lleva un comentario `# O(...)` con su Big-O real,
justo encima de su `def`, y siempre usa `n` como variable:

- O(1) = operaciones sobre campos escalares.
- O(n) = recorrido de n caracteres de texto o de n nodos o claves.

Ningún método supera O(n): los recorridos de cola y pila son simples
(secuenciales, nunca anidados) y los históricos usan acceso directo por clave.
