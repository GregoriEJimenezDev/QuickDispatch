"""Pruebas de extremo a extremo de la interfaz de consola por stdin."""
import os
import subprocess
import sys
import unittest

APP = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "main.py")
COLUMNS = "120"


# O(n): n = longitud de la entrada; lanza la app y devuelve código y salida.
def ejecutar(entrada: str, timeout: int = 60) -> tuple[int, str]:
    """Ejecuta la app por stdin con un ancho de terminal fijo."""
    env = {k: v for k, v in os.environ.items() if k not in ("COLUMNS", "LINES")}
    env.update(COLUMNS=COLUMNS, PYTHONUTF8="1", PYTHONIOENCODING="utf-8",
               PYTHONDONTWRITEBYTECODE="1")
    proceso = subprocess.run([sys.executable, APP], input=entrada, capture_output=True,
                             text=True, encoding="utf-8", errors="replace", env=env,
                             cwd=os.path.dirname(APP), timeout=timeout)
    return proceso.returncode, (proceso.stdout or "") + (proceso.stderr or "")


class CliFlowTests(unittest.TestCase):
    """Comprueba el menú de 6 opciones con entradas reales por teclado simulado."""

    # O(n): n = longitud del flujo; valida salida limpia y las 6 opciones.
    def test_flujo_completo_exit_cero(self) -> None:
        """Registrar, despachar, incidir, procesar, reportar y salir con S."""
        codigo, salida = ejecutar("1\nAna\nPerez\n3\n1\nLuis\nGarcia\n1\n2\n2\n"
                                  "3\na\n1\nmotivo\n4\n5\n6\nS\n")
        self.assertEqual(codigo, 0)
        self.assertNotIn("Traceback", salida)
        for opcion in range(1, 7):
            with self.subTest(opcion=opcion):
                self.assertIn(f"{opcion}. ", salida)
        self.assertIn("[OK] Incidencia Incident-0001 registrada en pila.", salida)
        self.assertIn("[OK] Incidencia Incident-0001 procesada.", salida)
        self.assertIn("Resumen final", salida)
        self.assertIn("Cierre sin excepciones. Hasta luego!", salida)

    # O(n): n = longitud de la salida; compara dos posiciones de texto.
    def test_despacho_fifo_visible_en_consola(self) -> None:
        """El primer pedido despachado aparece antes que el segundo."""
        codigo, salida = ejecutar("1\nAna\nPerez\n1\n1\nLuis\nGarcia\n1\n2\n2\n6\nS\n")
        self.assertEqual(codigo, 0)
        primero = salida.find("Pedido Order-0001 despachado")
        segundo = salida.find("Pedido Order-0002 despachado")
        self.assertNotEqual(primero, -1)
        self.assertLess(primero, segundo)

    # O(n): n = longitud de la salida; revisa los dos mensajes de error.
    def test_opcion_invalida_y_despacho_sin_cola(self) -> None:
        """Opción fuera de rango y cola vacía responden con [ERROR]."""
        codigo, salida = ejecutar("9\n2\n6\nN\n")
        self.assertEqual(codigo, 0)
        self.assertIn("[ERROR] Opción inválida. Elija 1-6.", salida)
        self.assertIn("[ERROR] No hay pedidos pendientes por despachar.", salida)
        self.assertIn("Salida cancelada.", salida)

    # O(n): n = longitud de la salida; confirma ambas ramas de salida.
    def test_salir_con_n_y_con_s(self) -> None:
        """N cancela sin resumen y S cierra con el resumen final."""
        _, salida_n = ejecutar("6\nN\n")
        self.assertIn("Salida cancelada.", salida_n)
        self.assertNotIn("Resumen final", salida_n)
        codigo, salida_s = ejecutar("6\nS\n")
        self.assertEqual(codigo, 0)
        self.assertIn("Resumen final", salida_s)
        self.assertIn("Pendientes: 0", salida_s)

    # O(1): cierra la entrada estándar en el menú principal.
    def test_eof_cierra_sin_traceback(self) -> None:
        """La entrada vacía cierra el menú limpiamente."""
        codigo, salida = ejecutar("")
        self.assertEqual(codigo, 0)
        self.assertNotIn("Traceback", salida)
        self.assertIn("Ejecucion interrumpida. Hasta luego!", salida)

    # O(n): n = longitud de los textos probados; distingue los tres errores.
    def test_mensajes_de_validacion_de_cantidad(self) -> None:
        """No numéricos, cero y más de 9 dígitos tienen mensajes propios."""
        codigo, salida = ejecutar("1\nAna\nPerez\nabc\n0\n1234567890\n7\n6\nS\n")
        self.assertEqual(codigo, 0)
        self.assertIn("[ERROR] Solo se permiten números enteros mayores que 0.", salida)
        self.assertIn("[ERROR] Ingrese un entero mayor que 0 de hasta 9 dígitos.",
                      salida)
        self.assertIn("[OK] Pedido Order-0001 registrado en cola.", salida)

    # O(n): n = longitud del flujo; intenta incidir sobre un pedido pendiente.
    def test_incidencia_sobre_pedido_pendiente(self) -> None:
        """Informa el estado real en vez de decir que no existe."""
        codigo, salida = ejecutar("1\nAna\nPerez\n2\n3\na\n-0001\nmotivo\n6\nS\n")
        self.assertEqual(codigo, 0)
        self.assertIn("[ERROR] Pedido Order-0001 no está DESPACHADO; "
                      "estado actual: PENDIENTE.", salida)
        self.assertNotIn("no existe en despachados", salida)


if __name__ == "__main__":
    unittest.main()
