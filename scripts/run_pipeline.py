"""Ejecuta la reconstrucción completa desde la raíz del repositorio."""

from pathlib import Path

from saldo_forestal.pipeline import ejecutar_pipeline


if __name__ == "__main__":
    repo = Path(__file__).resolve().parents[1]
    productos = ejecutar_pipeline(repo_dir=repo)
    print(f"Pipeline completo: {len(productos) - 2} tablas y {productos['zip']}")
