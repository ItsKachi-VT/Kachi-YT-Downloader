import os
import shutil
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DIST_DIR = BASE_DIR / "dist"
BUILD_DIR = BASE_DIR / "build"
SPEC_FILE = BASE_DIR / "app.spec"
FRONTEND_DIR = BASE_DIR / "frontend"


def run_command(command):
    print(f"Ejecutando: {' '.join(command)}")
    result = subprocess.run(command, cwd=str(BASE_DIR), text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Comando fallido con código {result.returncode}: {' '.join(command)}")


def clean_previous_builds():
    for folder in (DIST_DIR, BUILD_DIR):
        if folder.exists():
            shutil.rmtree(folder)
    if SPEC_FILE.exists():
        SPEC_FILE.unlink()


def build_app():
    clean_previous_builds()

    command = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--onefile",
        "--windowed",
        "--name",
        "KachiDownloader",
        "--add-data",
        f"{FRONTEND_DIR};frontend",
        "app.py",
    ]

    run_command(command)
    exe_path = DIST_DIR / "KachiDownloader.exe"
    if not exe_path.exists():
        raise FileNotFoundError(f"No se encontró el exe generado: {exe_path}")

    print(f"\nInstalador listo: {exe_path}")


if __name__ == "__main__":
    build_app()
