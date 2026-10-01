import re
import shutil
import textwrap

COLUMN_WIDTH = 100

_DATETIME_SEP = re.compile(r"(\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}:\d{2})")
_FECHA_DATE = re.compile(r"Fecha: (\d{4}-\d{2}-\d{2})")
_WORD_JOINER = chr(0x2060)
_FIELD_SEP = " | "


# O(1): ancho de la terminal en vivo (80 si no se detecta).
def term_width() -> int:
    """Devuelve el ancho actual de la terminal."""
    try:
        return shutil.get_terminal_size().columns
    except Exception:
        return 80


# O(1): ancho de la columna de contenido (100, adaptado a la terminal, mínimo 40).
def column_width() -> int:
    """Devuelve el ancho de la columna centrada."""
    return max(40, min(COLUMN_WIDTH, term_width() - 2))


# O(1): espacios a la izquierda de la columna de contenido.
def margin() -> int:
    """Calcula el margen izquierdo de la columna."""
    return max(0, (term_width() - column_width()) // 2)


# O(n): n = longitud del texto; lo centra dentro del ancho de la columna.
def centered(text: str) -> str:
    """Centra un texto dentro de la columna."""
    return " " * margin() + str(text).center(column_width())


# O(1): repite un carácter con el ancho fijo de la columna (sin entrada variable).
def line(char: str = "=") -> str:
    """Crea una línea horizontal de la columna."""
    return " " * margin() + char * column_width()


# O(n): n = longitud del mensaje; escribe sus n caracteres en consola.
def show(message: str = "") -> None:
    """Imprime una línea en consola."""
    print(str(message))


# O(n): n = longitud del título; lo centra e imprime entre dos líneas.
def title(text: str) -> None:
    """Imprime un título centrado entre líneas."""
    show("")
    show(line("="))
    show(centered(str(text).upper()))
    show(line("="))


# O(n): n = longitud del subtítulo; lo centra e imprime entre guiones.
def section(text: str) -> None:
    """Imprime un subtítulo centrado."""
    show("")
    show(centered("-- " + str(text) + " --"))


# O(n): ajusta una línea partiendo SOLO en " | " (n = caracteres de la línea).
def _wrap_line(text: str, width: int) -> list[str]:
    """Corta una línea solo en ' | ', sin partir campos ni 'Fecha:' y su valor."""
    fields = text.split(_FIELD_SEP)
    if len(fields) == 1:
        shielded = _DATETIME_SEP.sub(lambda m: m.group(1) + _WORD_JOINER + m.group(2), text)
        shielded = _FECHA_DATE.sub(lambda m: "Fecha:" + _WORD_JOINER + m.group(1), shielded)
        parts = textwrap.wrap(shielded, width=width, subsequent_indent="  ",
                              break_on_hyphens=False) or [""]
        return [part.replace(_WORD_JOINER, " ") for part in parts]
    out: list[str] = []
    current = fields[0]
    for field in fields[1:]:
        indent = 2 if out else 0
        if len(current) + len(_FIELD_SEP) + len(field) <= width - indent:
            current = current + _FIELD_SEP + field
        else:
            out.append(current)
            current = field
    out.append(current)
    return [out[0]] + ["  " + part for part in out[1:]]


# O(n): n = caracteres totales del bloque; ajusta e imprime sus n caracteres.
def show_block(lines: list[str], align: str = "left") -> None:
    """Imprime líneas ajustadas dentro de la columna."""
    width = column_width()
    wrapped: list[str] = []
    for text in lines:
        wrapped.extend(_wrap_line(str(text), width))
    if align == "block":
        longest = 0
        for part in wrapped:
            longest = max(longest, len(part))
        pad = " " * (margin() + (width - longest) // 2)
        for part in wrapped:
            show(pad + part.ljust(longest))
    else:
        pad = " " * margin()
        for part in wrapped:
            show(pad + part)


# O(n): n = longitud de la línea leída; la recorta y la devuelve sin espacios.
def read_text(prompt: str) -> str:
    """Lee texto recortado desde consola."""
    text = input(" " * margin() + "  " + prompt + " ").strip()
    show("")
    return text


# O(n) por intento: n = longitud del texto; valida largo <= 9 ANTES de int().
def read_positive_int(prompt: str) -> int:
    """Lee un entero mayor que 0 de hasta 9 dígitos, repitiendo si hace falta."""
    base = " " * margin() + "  " + prompt + " "
    while True:
        text = input(base).strip()
        show("")
        if 0 < len(text) <= 9 and text.isdecimal() and int(text) > 0:
            return int(text)
        show(centered("[ERROR] Solo se permiten números enteros mayores que 0."))


# O(n): n = longitud del texto; recorre sus n caracteres buscando solo letras.
def _letters_ok(text: str) -> bool:
    """Indica si el texto solo tiene letras."""
    clean = text.strip()
    if not any(c.isalpha() for c in clean):
        return False
    return all(c.isalpha() or c in " -'" for c in clean)


# O(n) por intento: n = longitud del texto; repite hasta recibir solo letras.
def read_letters(prompt: str) -> str:
    """Lee solo letras, repitiendo si hace falta."""
    base = " " * margin() + "  " + prompt + " "
    while True:
        text = input(base).strip()
        show("")
        if _letters_ok(text):
            return text
        show(centered("[ERROR] Solo se permiten letras en este campo. Intente de nuevo."))
