"""Ejecuta la reconstrucción completa desde la raíz del repositorio."""

from pathlib import Path

from saldo_forestal.reproduccion import ejecutar_reproduccion


if __name__ == "__main__":
    repo = Path(__file__).resolve().parents[1]
    productos = ejecutar_reproduccion(repo_dir=repo)
    print(f"Reproducción completa: {len(productos) - 2} productos y {productos['zip']}")
