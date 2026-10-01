"""Pruebas de la cola FIFO y de la pila LIFO sobre lista enlazada simple."""
import unittest

from data_structures.queue_linked_list import QueueLinkedList
from data_structures.stack_linked_list import StackLinkedList


class QueueLinkedListTests(unittest.TestCase):
    """Comprueba FIFO, las referencias front/rear y el vaciado correcto."""

    # O(1): crea una cola vacía para cada prueba.
    def setUp(self) -> None:
        """Prepara una cola nueva por prueba."""
        self.queue = QueueLinkedList()

    # O(1): inserta tres nodos y consulta los dos extremos.
    def test_enqueue_mantiene_front_y_rear(self) -> None:
        """El frente es el primero y el final el último insertado."""
        self.queue.enqueue("a")
        self.queue.enqueue("b")
        self.queue.enqueue("c")
        front, rear = self.queue._front, self.queue._rear
        assert front is not None and rear is not None
        self.assertEqual(front.data, "a")
        self.assertEqual(rear.data, "c")
        self.assertEqual(len(self.queue), 3)

    # O(n): n = 3 elementos extraídos en orden de llegada.
    def test_dequeue_respeta_fifo(self) -> None:
        """Extrae siempre el elemento más antiguo."""
        for item in ("a", "b", "c"):
            self.queue.enqueue(item)
        extraidos = [self.queue.dequeue() for _ in range(3)]
        self.assertEqual(extraidos, ["a", "b", "c"])

    # O(1): comprueba la limpieza de ambas referencias al vaciarse.
    def test_vaciar_deja_front_y_rear_en_none(self) -> None:
        """Al consumir todo, no queda ninguna referencia colgando."""
        self.queue.enqueue("a")
        self.queue.dequeue()
        self.assertTrue(self.queue.is_empty())
        self.assertIsNone(self.queue._front)
        self.assertIsNone(self.queue._rear)

    # O(1): extraer de la cola vacía devuelve None sin excepción.
    def test_dequeue_en_cola_vacia(self) -> None:
        """La cola vacía responde None en lugar de fallar."""
        self.assertIsNone(self.queue.dequeue())

    # O(1): el rear se reconstruye si se inserta tras haberse vaciado.
    def test_rear_no_queda_obsoleto(self) -> None:
        """Insertar tras vaciar vuelve a funcionar con normalidad."""
        self.queue.enqueue("x")
        self.queue.dequeue()
        self.queue.enqueue("y")
        self.assertEqual(self.queue.dequeue(), "y")
        self.assertIsNone(self.queue._rear)

    # O(1): el recorrido respeta el orden de inserción.
    def test_traverse_forward_en_fifo(self) -> None:
        """El recorrido va del frente al final."""
        self.queue.enqueue("p")
        self.queue.enqueue("r")
        self.assertEqual(list(self.queue.traverse_forward()), ["p", "r"])

    # O(1): inspecciona los atributos internos del objeto.
    def test_usa_nodos_y_no_listas_nativas(self) -> None:
        """La cola no se apoya en una lista de Python."""
        self.assertFalse(any(isinstance(v, list) for v in self.queue.__dict__.values()))


class StackLinkedListTests(unittest.TestCase):
    """Comprueba LIFO, la referencia top y el vaciado correcto."""

    # O(1): crea una pila vacía para cada prueba.
    def setUp(self) -> None:
        """Prepara una pila nueva por prueba."""
        self.stack = StackLinkedList()

    # O(1): inserta tres nodos y consulta la cima.
    def test_push_mantiene_top(self) -> None:
        """La cima es el último elemento insertado."""
        self.stack.push(1)
        self.stack.push(2)
        self.stack.push(3)
        top = self.stack._top
        assert top is not None
        self.assertEqual(top.data, 3)
        self.assertEqual(len(self.stack), 3)

    # O(n): n = 3 elementos extraídos en orden inverso al de entrada.
    def test_pop_respeta_lifo(self) -> None:
        """Extrae siempre el elemento más reciente."""
        for item in (1, 2, 3):
            self.stack.push(item)
        extraidos = [self.stack.pop() for _ in range(3)]
        self.assertEqual(extraidos, [3, 2, 1])

    # O(1): extraer de la pila vacía devuelve None sin excepción.
    def test_pop_en_pila_vacia(self) -> None:
        """La pila vacía responde None en lugar de fallar."""
        self.assertIsNone(self.stack.pop())
        self.assertTrue(self.stack.is_empty())

    # O(n): n = 3 incidencias apiladas, recorridas de la cima a la base.
    def test_traverse_from_top_en_lifo(self) -> None:
        """El recorrido sale de la cima hacia abajo."""
        for item in ("i1", "i2", "i3"):
            self.stack.push(item)
        self.assertEqual(list(self.stack.traverse_from_top()), ["i3", "i2", "i1"])

    # O(1): inspecciona los atributos internos del objeto.
    def test_usa_nodos_y_no_listas_nativas(self) -> None:
        """La pila no se apoya en una lista de Python."""
        self.assertFalse(any(isinstance(v, list) for v in self.stack.__dict__.values()))


if __name__ == "__main__":
    unittest.main()
