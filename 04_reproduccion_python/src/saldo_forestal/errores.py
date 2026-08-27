"""Excepciones de dominio con mensajes metodológicos explícitos."""


class DominiosSuperpuestosError(ValueError):
    """Se intentó agregar resultados construidos sobre unidades superpuestas."""
