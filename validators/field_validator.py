from typing import Any, Optional

from models.operation_result import OperationResult


# O(1): validacion escalar de texto no vacio.
def rule_required(value: Any, field_name: str) -> Optional[str]:
    """Exige texto no vacío."""
    if value is None:
        return f"{field_name} es obligatorio."
    if isinstance(value, str) and value.strip() == "":
        return f"{field_name} es obligatorio."
    return None


# O(1): validacion escalar de entero positivo.
def rule_positive_int(value: Any, field_name: str) -> Optional[str]:
    """Exige un entero mayor que cero."""
    if not isinstance(value, int) or isinstance(value, bool):
        return f"{field_name} debe ser un número entero."
    if value <= 0:
        return f"{field_name} debe ser mayor que 0."
    return None


# O(1): validacion escalar contra un conjunto fijo de opciones.
def rule_choice(value: Any, field_name: str, choices: tuple[str, ...]) -> Optional[str]:
    """Exige un valor de la lista permitida."""
    if value not in choices:
        return f"{field_name} debe ser uno de: {', '.join(choices)}."
    return None


# O(m): solo letras unicode (acepta tildes y enie), espacios, guiones y apostrofes.
def rule_letters_only(value: Any, field_name: str) -> Optional[str]:
    """Exige solo letras y signos básicos."""
    text = value.strip() if isinstance(value, str) else ""
    if not any(c.isalpha() for c in text):
        return f"{field_name} solo debe contener letras."
    for c in text:
        if not (c.isalpha() or c in " -'"):
            return f"{field_name} solo debe contener letras."
    return None


class FieldValidator:
    """Valida campos con reglas inyectables."""

    # O(1): guarda referencias a reglas inyectadas.
    def __init__(self, extra_rules: list | None = None) -> None:
        """Guarda las reglas extra recibidas."""
        self.extra_rules = list(extra_rules) if extra_rules else []

    # O(k + m): reglas extra (k) + barrido de letras sobre el texto (m, su longitud).
    def validate_order_fields(self, nombre: str, apellido: str, cajas: int) -> OperationResult:
        """Valida nombre, apellido y cajas."""
        error = rule_required(nombre, "Nombre")
        if error:
            return OperationResult.failure(error)
        error = rule_letters_only(nombre, "Nombre")
        if error:
            return OperationResult.failure(error)
        error = rule_required(apellido, "Apellido")
        if error:
            return OperationResult.failure(error)
        error = rule_letters_only(apellido, "Apellido")
        if error:
            return OperationResult.failure(error)
        error = rule_positive_int(cajas, "Cantidad de cajas")
        if error:
            return OperationResult.failure(error)
        for rule in self.extra_rules:
            error = rule({"nombre": nombre, "apellido": apellido, "cajas": cajas})
            if error:
                return OperationResult.failure(error)
        return OperationResult.success(message="Campos de pedido validos.")

    # O(k): recorre las k reglas extra inyectadas (k acotado, no depende de n).
    def validate_incident_fields(self, tipo: str, order_id: str, motivo: str,
                                 tipos_validos: tuple[str, ...]) -> OperationResult:
        """Valida tipo, pedido y motivo."""
        error = rule_required(tipo, "Tipo")
        if error:
            return OperationResult.failure(error)
        error = rule_choice(tipo, "Tipo", tipos_validos)
        if error:
            return OperationResult.failure(error)
        error = rule_required(order_id, "Order ID")
        if error:
            return OperationResult.failure(error)
        error = rule_required(motivo, "Motivo")
        if error:
            return OperationResult.failure(error)
        for rule in self.extra_rules:
            error = rule({"tipo": tipo, "order_id": order_id, "motivo": motivo})
            if error:
                return OperationResult.failure(error)
        return OperationResult.success(message="Campos de incidencia validos.")
