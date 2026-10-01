Los pedidos pendientes viven en una cola FIFO (lista enlazada simple con front y rear).
Las incidencias pendientes (devoluciones/cancelaciones) viven en una pila LIFO (lista enlazada simple con top).
Los pedidos despachados y las incidencias procesadas se guardan como históricos en diccionarios nativos.
Cómo ejecutar
bash
cd QuickDispatch
python main.py

Requiere Python 3.10 o superior (se usa X | None en las anotaciones de tipo). No tiene dependencias de terceros.

La interfaz usa una columna centrada de 100 caracteres (se adapta al ancho de la terminal, con un mínimo de 40). Conviene maximizar o ajustar la ventana antes de ejecutar y no cambiar su tamaño durante la sesión.

Menú principal
Opción	Qué hace
1. Registrar pedido	Pide nombre, apellido y cantidad de cajas; genera el Order ID y encola el pedido (enqueue).
2. Despachar pedido	Retira el pedido más antiguo de la cola (dequeue), lo marca DESPACHADO y lo guarda en el histórico. No pide datos.
3. Registrar devolución/cancelación	Pide tipo (a: DEVOLUCIÓN, b: CANCELACIÓN), Order ID y motivo; apila la incidencia (push).
4. Procesar devolución/cancelación	Retira la incidencia más reciente de la pila (pop), la marca PROCESADA y cierra el pedido. No pide datos.
5. Ver estado (reporte completo)	Muestra la cola, los despachados, la pila y las incidencias procesadas.
6. Salir	Pide confirmación S/N y muestra el resumen final.
Reglas de negocio

Pedidos

El Order ID se genera solo (Order-0001, Order-0002, ...), es único y nunca se reutiliza, ni siquiera cuando el pedido ya está despachado o cerrado.
Nombre y apellido son obligatorios y solo admiten letras, espacios, guiones y apóstrofes.
La cantidad de cajas es un entero mayor que 0 de hasta 9 dígitos. Si el dato es inválido, la interfaz lo vuelve a pedir con un mensaje propio para cada caso.
La fecha y hora se asignan automáticamente y el estado inicial es PENDIENTE.
Un mismo cliente puede registrar varios pedidos: lo único único es el Order ID.

Incidencias

Solo se puede registrar una incidencia sobre un pedido DESPACHADO (debe existir en el histórico de despachados). Un pedido pendiente, inexistente o CERRADO se rechaza con un mensaje.
Un pedido solo puede tener una incidencia pendiente a la vez.
Al registrar, el pedido pasa a DEVUELTO (devolución) o CANCELADO (cancelación).
Al procesar, la incidencia pasa a PROCESADA y el pedido a CERRADO. El pedido permanece en el histórico de despachados con su estado final.
El Incident ID también se autogenera (Incident-0001, ...) y es único.
Al pedir el Order ID se aceptan Order-0001 (sin distinguir mayúsculas), 1 y 0001. También se acepta -0001, pero solo si ese pedido existe.

Ciclo de estados

text
Pedido:      PENDIENTE -> DESPACHADO -> DEVUELTO | CANCELADO -> CERRADO
Incidencia:  PENDIENTE -> PROCESADA

Salir

Se pide confirmación (S/N). Con S se muestra el resumen final (pedidos pendientes y despachados, incidencias pendientes y procesadas) y el programa termina sin errores.
Con N, o con cualquier otra respuesta, la salida se cancela y se vuelve al menú.
Ctrl+C y el fin de entrada (EOF) también cierran el programa sin mostrar un traceback.
Pruebas
bash
cd QuickDispatch
python -m unittest discover -v

tests/ contiene pruebas automáticas con unittest (biblioteca estándar, sin dependencias): cola FIFO y pila LIFO, registro y despacho de pedidos, registro y procesamiento de incidencias, y flujos completos de la interfaz por stdin (salida limpia, EOF, mensajes de validación y despacho en orden FIFO).

Estructura de carpetas
main.py: composición de dependencias (build_app) y entrada (main).
models/: entidades Order e Incident, enums (enums.py), nodo Node.
models/operation_result.py: retorno único OperationResult de cada operación.
data_structures/: cola FIFO (front/rear) y pila LIFO (top) con lista enlazada simple.
orders/ e incidents/: factories, builders y servicios de cada flujo.
validators/: reglas de validación inyectables.
ui/: utilidades de consola y menú principal de 6 opciones.
tests/: pruebas automáticas con unittest (cola, pila, pedidos, incidencias y CLI).
requirements.txt: nota de versión mínima de Python (sin dependencias).
Justificación de estructuras de datos

Queue (cola) para pedidos. Se despacha por orden de llegada (FIFO): el primero registrado es el primero despachado, que es la regla de negocio de reparto. Con front y rear, enqueue, dequeue y peek son O(1) y no dependen del tamaño de la cola.

Stack (pila) para incidencias. Se atiende primero la más reciente (LIFO): el último reclamo es el más urgente y debe resolverse antes que los anteriores. Con top, push, pop y peek son O(1) sin recorrer nodos.

Por qué lista enlazada simple. Insertar y extraer en cualquier extremo cuesta O(1) con dos referencias (front/rear) o una (top): solo se enlaza o desenlaza el nodo afectado y se actualiza el contador, sin reasignar memoria de un bloque contiguo ni desplazar elementos como haría una lista nativa al insertar al inicio. Los históricos de pedidos despachados e incidencias procesadas usan acceso directo por clave en diccionarios nativos.

Complejidades por operación

Cola FIFO (QueueLinkedList):

Operación	Complejidad	Por qué
enqueue(dato)	O(1)	enlaza el nodo nuevo en rear y fija front si estaba vacía
dequeue()	O(1)	extrae el nodo de front y avanza la referencia
peek()	O(1)	lee front sin extraer
is_empty() / len()	O(1)	contador incremental _size
traverse_forward()	O(n)	recorre los n nodos desde front, sin copiarlos

Pila LIFO (StackLinkedList):

Operación	Complejidad	Por qué
push(dato)	O(1)	enlaza el nodo nuevo como top
pop()	O(1)	extrae el nodo de top y avanza la referencia
peek()	O(1)	lee top sin extraer
is_empty() / len()	O(1)	contador incremental _size
traverse_from_top()	O(n)	recorre los n nodos desde top, sin copiarlos

Ninguna operación supera O(n) y ningún recorrido está anidado con otro. Los listados del reporte recorren los nodos de la lista enlazada; no se copian a listas nativas.

Factory y Builder

Viven en orders/ (OrderFactory, OrderBuilder) e incidents/ (IncidentFactory, IncidentBuilder). Se reparten el trabajo: el Builder recibe y normaliza la entrada (strip, mayúsculas, alias sin tilde) con setters encadenables (with_nombre, with_apellido, with_cajas, with_tipo, with_order_id, with_motivo); la Factory valida, emite el ID único (Order-0001, Incident-0001), asigna fecha y estado, e instancia el modelo. Los estados y tipos son enums (OrderStatus, IncidentStatus, IncidentType).

Convención de complejidad

Cada método y función lleva un comentario # O(...) con su Big-O real, justo encima de su def, y siempre usa n como variable:

O(1) = operaciones sobre campos escalares.
O(n) = recorrido de n caracteres de texto o de n nodos o claves.

Ningún método supera O(n): los recorridos de cola y pila son simples (secuenciales, nunca anidados) y los históricos usan acceso directo por clave.