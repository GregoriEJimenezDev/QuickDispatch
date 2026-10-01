import shutil

CONTENT = 64


# O(1): ancho de la terminal en vivo (80 si no se detecta).
def term_width() -> int:
    """Devuelve el ancho actual de la terminal."""
    try:
        return shutil.get_terminal_size().columns
    except Exception:
        return 80


# O(1): espacios a la izquierda para centrar el bloque de contenido.
def margin(width: int = CONTENT) -> int:
    """Calcula el margen izquierdo para centrar."""
    return max(0, (term_width() - width) // 2)


# O(1): centra un texto en el ancho real de la terminal.
def centered(text: str) -> str:
    """Centra un texto en la terminal."""
    return str(text).center(max(term_width(), len(str(text))))


# O(1): linea horizontal de 64, centrada en la terminal real.
def line(char: str = "=") -> str:
    """Crea una línea horizontal centrada."""
    return centered(char * CONTENT)


# O(1): imprime una linea tal cual.
def show(message: str = "") -> None:
    """Imprime una línea en consola."""
    print(str(message))


# O(1): titulo centrado.
def title(text: str) -> None:
    """Imprime un título centrado entre líneas."""
    show("")
    show(line("="))
    show(centered(str(text).upper()))
    show(line("="))


# O(1): subtitulo centrado entre guiones.
def section(text: str) -> None:
    """Imprime un subtítulo centrado."""
    show("")
    show(centered("-- " + str(text) + " --"))


# O(n): bloque alineado a la columna izquierda compartida (n = lineas).
def show_block(lines: list[str]) -> None:
    """Imprime líneas alineadas en la columna de contenido."""
    width = 0
    for text in lines:
        width = max(width, len(str(text)))
    pad = " " * margin()
    for text in lines:
        show(pad + str(text).ljust(width))


# O(1): lee una linea y la devuelve sin espacios externos.
def read_text(prompt: str) -> str:
    """Lee texto recortado desde consola."""
    return input(" " * margin() + "  " + prompt + " ").strip()


# O(m) por intento: re-pide hasta recibir un entero mayor que 0 (m = largo del texto).
def read_positive_int(prompt: str) -> int:
    """Lee un entero mayor que 0, repitiendo si hace falta."""
    base = " " * margin() + "  " + prompt + " "
    while True:
        text = input(base).strip()
        if text.isdecimal() and int(text) > 0:
            return int(text)
        show(centered("[ERROR] Solo se permiten números enteros mayores que 0."))


# O(m): verifica solo-letras para re-pedir el dato sin avanzar (m = largo del texto).
def _letters_ok(text: str) -> bool:
    """Indica si el texto solo tiene letras."""
    clean = text.strip()
    if not any(c.isalpha() for c in clean):
        return False
    return all(c.isalpha() or c in " -'" for c in clean)


# O(m) por intento: re-pide por consola hasta recibir solo letras (m = largo del texto).
def read_letters(prompt: str) -> str:
    """Lee solo letras, repitiendo si hace falta."""
    base = " " * margin() + "  " + prompt + " "
    while True:
        text = input(base).strip()
        if _letters_ok(text):
            return text
        show(centered("[ERROR] Solo se permiten letras en este campo. Intente de nuevo."))
