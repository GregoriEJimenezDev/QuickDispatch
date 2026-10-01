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


