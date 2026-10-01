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

## Estructura de carpetas

- `main.py`: composición de dependencias (`build_app`) y entrada (`main`).
- `models/`: entidades `Order` e `Incident`, enums (`enums.py`), nodo `Node`.
- `models/operation_result.py`: retorno único `OperationResult` de cada operación.
- `data_structures/`: cola FIFO (`front`/`rear`) y pila LIFO (`top`) con lista enlazada.
- `orders/` e `incidents/`: factories, builders y servicios de cada flujo.
- `validators/`: reglas de validación inyectables.
- `ui/`: utilidades de consola y menú principal de 6 opciones.

## Por qué pila para incidencias

Se atiende primero la más reciente (LIFO): el último reclamo es el más urgente.
`push`, `pop` y `peek` son O(1) sobre `top`, sin recorrer nodos.

## Por qué cola para pedidos

Se despacha por orden de llegada (FIFO): el primero registrado es el primero
despachado. `enqueue`, `dequeue` y `peek` son O(1) con `front` y `rear`.

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

Cada método y función lleva un comentario `# O(...)` con su Big-O real:

- O(1) = operaciones sobre campos escalares.
- O(m) = recorrido de un texto de longitud m.
- O(n) = recorrido de n nodos o claves de una estructura.

Ningún método supera O(n): los recorridos de cola y pila son simples
(secuenciales, nunca anidados) y los históricos usan acceso directo por clave.


