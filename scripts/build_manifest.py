"""Genera el inventario público de tamaño y SHA-256 de cada artefacto."""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path


EXCLUIR_DIRECTORIOS = {
    ".git",
    ".venv",
    ".pytest_cache",
    "__pycache__",
    ".ipynb_checkpoints",
    "build",
    "dist",
}
EXCLUIR_ARCHIVOS = {"manifiesto_archivos.csv", "manifiesto_archivos.txt"}


def sha256(ruta: Path) -> str:
    digest = hashlib.sha256()
    with ruta.open("rb") as archivo:
        for bloque in iter(lambda: archivo.read(1024 * 1024), b""):
            digest.update(bloque)
    return digest.hexdigest()


def construir(raiz: Path) -> list[dict[str, str | int]]:
    filas = []
    for ruta in sorted(raiz.rglob("*")):
        if not ruta.is_file():
            continue
        relativa = ruta.relative_to(raiz)
        if any(
            parte in EXCLUIR_DIRECTORIOS or parte.endswith(".egg-info")
            for parte in relativa.parts
        ):
            continue
        if ruta.name in EXCLUIR_ARCHIVOS:
            continue
        filas.append(
            {
                "ruta": relativa.as_posix(),
                "bytes": ruta.stat().st_size,
                "sha256": sha256(ruta),
            }
        )
    return filas


def escribir(raiz: Path, filas: list[dict[str, str | int]]) -> None:
    with (raiz / "manifiesto_archivos.csv").open("w", encoding="utf-8", newline="") as archivo:
        escritor = csv.DictWriter(
            archivo,
            fieldnames=["ruta", "bytes", "sha256"],
            lineterminator="\n",
        )
        escritor.writeheader()
        escritor.writerows(filas)
    texto = "".join(f"{fila['sha256']}  {fila['ruta']}\n" for fila in filas)
    (raiz / "manifiesto_archivos.txt").write_text(texto, encoding="utf-8")


if __name__ == "__main__":
    repo = Path(__file__).resolve().parents[1]
    registros = construir(repo)
    escribir(repo, registros)
    print(f"Manifiesto generado para {len(registros)} archivos.")
