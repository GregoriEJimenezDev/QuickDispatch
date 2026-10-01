from typing import Any


class OperationResult:
    """Resultado único de cada operación de negocio."""

    # O(1): solo asigna tres atributos.
    def __init__(self, ok: bool, data: Any = None, message: str = "") -> None:
        """Guarda ok, data y message."""
        self.ok = ok
        self.data = data
        self.message = message

    # O(1): formateo de una linea.
    def __repr__(self) -> str:
        """Muestra el resultado en una línea."""
        return f"OperationResult(ok={self.ok}, message={self.message!r})"

    # O(1): fabrica de exito.
    @staticmethod
    def success(data: Any = None, message: str = "") -> "OperationResult":
        """Crea un resultado de éxito."""
        return OperationResult(True, data, message)

    # O(1): fabrica de fallo esperado (sin excepciones).
    @staticmethod
    def failure(message: str, data: Any = None) -> "OperationResult":
        """Crea un resultado de fallo esperado."""
        return OperationResult(False, data, message)
