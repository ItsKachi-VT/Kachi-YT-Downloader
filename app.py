import json
import os
import shutil
import subprocess
import sys
import threading
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

import webview
import yt_dlp

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "frontend"
HISTORY_FILE = BASE_DIR / "history.json"
STATE = {
    "status": "idle",
    "detail": "Listo para descargar.",
    "progress": 0,
    "error": "",
}
STATE_LOCK = threading.Lock()


def set_state(status: str, detail: str, progress: int = 0, error: str = ""):
    global STATE
    with STATE_LOCK:
        STATE["status"] = status
        STATE["detail"] = detail
        STATE["progress"] = progress
        STATE["error"] = error


def normalize_output_dir(path: str | None) -> str:
    if path and path.strip():
        p = Path(path).expanduser()
        try:
            p.mkdir(parents=True, exist_ok=True)
            return str(p)
        except OSError:
            fallback = get_downloads_dir() / "Kachi Downloader"
            fallback.mkdir(parents=True, exist_ok=True)
            return str(fallback)
    default = get_downloads_dir() / "Kachi Downloader"
    default.mkdir(parents=True, exist_ok=True)
    return str(default)


def get_downloads_dir() -> Path:
    candidates = [
        Path.home() / "Downloads",
        Path.home() / "Desktop",
        Path.home(),
    ]

    for candidate in candidates:
        try:
            candidate.mkdir(parents=True, exist_ok=True)
            if os.access(candidate, os.W_OK):
                return candidate
        except OSError:
            continue

    return Path.home()


def validate_url(url: str) -> bool:
    if not url or not url.strip():
        return False
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        return False
    if not parsed.netloc:
        return False
    return True


def find_ffmpeg() -> str | None:
    candidates = [
        shutil.which("ffmpeg"),
        shutil.which("ffmpeg.exe"),
        str(Path("C:/ffmpeg/bin/ffmpeg.exe")),
        str(Path("C:/Program Files/ffmpeg/bin/ffmpeg.exe")),
        str(Path("C:/Program Files (x86)/ffmpeg/bin/ffmpeg.exe")),
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return candidate
    return None


def ensure_ffmpeg() -> str:
    ffmpeg = find_ffmpeg()
    if ffmpeg:
        return ffmpeg

    if os.name == "nt":
        winget = shutil.which("winget")
        if winget:
            try:
                subprocess.run(
                    [
                        winget,
                        "install",
                        "-e",
                        "--id",
                        "Gyan.FFmpeg",
                        "--accept-source-agreements",
                        "--accept-package-agreements",
                    ],
                    check=False,
                    capture_output=True,
                    text=True,
                )
                ffmpeg = find_ffmpeg()
                if ffmpeg:
                    return ffmpeg
            except Exception:
                pass

    raise RuntimeError(
        "No se encontró FFmpeg. Instálalo desde https://www.ffmpeg.org/download.html o usa Winget."
    )


def ensure_ytdlp_exe() -> str:
    exe_path = BASE_DIR / "yt-dlp.exe"
    if exe_path.exists():
        return str(exe_path)

    url = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe"
    try:
        import requests

        response = requests.get(url, timeout=40)
        response.raise_for_status()
        exe_path.write_bytes(response.content)
        return str(exe_path)
    except Exception as exc:
        raise RuntimeError(
            "No se pudo descargar yt-dlp. Revisa tu conexión o instala la versión manualmente."
        ) from exc


def current_quality_options(output_format: str, resolution: str):
    if output_format == "audio_mp3":
        return {
            "format": "bestaudio/best",
            "merge_output_format": None,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "0",
                }
            ],
        }

    selected_resolution = resolution if resolution in {"1080", "720", "480", "360"} else "1080"
    selected_container = "mp4" if output_format == "video_mp4" else "mkv"
    return {
        "format": f"bestvideo[height<={selected_resolution}]+bestaudio/best",
        "merge_output_format": selected_container,
        "postprocessors": [],
    }


def ensure_history_file():
    if not HISTORY_FILE.exists():
        HISTORY_FILE.write_text("[]", encoding="utf-8")


def read_history():
    ensure_history_file()
    try:
        content = HISTORY_FILE.read_text(encoding="utf-8").strip()
        if not content:
            return []
        data = json.loads(content)
        return data if isinstance(data, list) else []
    except Exception:
        return []


def write_history(items):
    HISTORY_FILE.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")


def download_video(url: str, output_format: str, resolution: str, output_dir: str):
    set_state("preparing", "Validando URL y preparando la descarga...", 5)
    if not validate_url(url):
        raise ValueError("Debes ingresar una URL válida de YouTube o un enlace compatible.")

    output_path = normalize_output_dir(output_dir)
    ffmpeg_path = ensure_ffmpeg()
    ffmpeg_dir = str(Path(ffmpeg_path).parent)
    quality_opts = current_quality_options(output_format, resolution)

    options = {
        "format": quality_opts["format"],
        "outtmpl": str(Path(output_path) / "%(title)s.%(ext)s"),
        "noplaylist": True,
        "retries": 3,
        "fragment_retries": 3,
        "no_warnings": True,
        "continue": True,
        "ffmpeg_location": ffmpeg_dir,
        "paths": {"home": output_path},
        "postprocessors": quality_opts["postprocessors"],
        "merge_output_format": quality_opts["merge_output_format"],
        "quiet": False,
    }

    def progress_hook(d):
        if d.get("status") == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
            downloaded = d.get("downloaded_bytes") or 0
            if total and total > 0:
                progress = min(99, int((downloaded / total) * 100))
            else:
                progress = 0
            set_state("downloading", "Descargando archivo...", progress)
        elif d.get("status") == "finished":
            set_state("finishing", "Finalizando y procesando archivo...", 100)
        elif d.get("status") == "error":
            set_state("error", "La descarga falló. Intenta otra URL o revisa el enlace.", 0, "Error en la descarga")

    options["progress_hooks"] = [progress_hook]

    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=True)
        title = info.get("title", "archivo") if isinstance(info, dict) else "archivo"
        set_state("done", f"Descarga completada: {title}", 100, "")
        return {"ok": True, "title": title, "folder": output_path}
    except Exception as exc:  # pragma: no cover - UI error path
        error_text = str(exc)
        set_state("error", "No se pudo completar la descarga.", 0, error_text)
        raise RuntimeError(error_text) from exc


class AppApi:
    def request_downloads_access(self):
        default = get_downloads_dir()
        downloads_dir = default / "Kachi Downloader"
        downloads_dir.mkdir(parents=True, exist_ok=True)
        return str(downloads_dir)

    def select_folder(self):
        default = Path(self.request_downloads_access())
        try:
            import tkinter as tk
            from tkinter import filedialog

            root = tk.Tk()
            root.withdraw()
            root.attributes("-topmost", True)
            selected = filedialog.askdirectory(
                initialdir=str(default),
                title="Selecciona la carpeta donde guardar tus descargas",
            )
            root.destroy()
            if selected and selected.strip():
                selected_path = Path(selected)
                selected_path.mkdir(parents=True, exist_ok=True)
                if os.access(selected_path, os.W_OK):
                    return str(selected_path)
        except Exception:
            pass

        return str(default)

    def get_history(self):
        return read_history()

    def status(self):
        with STATE_LOCK:
            return dict(STATE)

    def download(self, url: str, output_format: str, resolution: str, folder: str):
        try:
            if not url or not url.strip():
                raise ValueError("Debes pegar un enlace antes de descargar.")
            if not validate_url(url):
                raise ValueError("La URL no parece válida. Verifica el enlace e intenta otra vez.")

            output_dir = normalize_output_dir(folder)
            result = download_video(url, output_format, resolution, output_dir)

            entry = {
                "url": url,
                "title": result.get("title", "Archivo descargado"),
                "tipo": "audio" if output_format == "audio_mp3" else "video",
                "formato": "MP3" if output_format == "audio_mp3" else ("MKV" if output_format == "video_mkv" else "MP4"),
                "resolucion": "Audio" if output_format == "audio_mp3" else resolution + "p",
                "ruta": output_dir,
                "fecha": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            }

            history = read_history()
            history.insert(0, entry)
            write_history(history[:25])

            return {"ok": True, "message": "Descarga completada", "data": result}
        except Exception as exc:
            error_message = str(exc)
            set_state("error", error_message, 0, error_message)
            return {"ok": False, "message": error_message}


def main():
    html_path = FRONTEND_DIR / "index.html"
    if not html_path.exists():
        raise FileNotFoundError(f"No se encontró la vista HTML en: {html_path}")

    api = AppApi()
    default_downloads = api.request_downloads_access()
    os.makedirs(default_downloads, exist_ok=True)

    window = webview.create_window(
        "Kachi Downloader",
        str(html_path),
        width=1100,
        height=760,
        resizable=True,
        min_size=(860, 620),
        maximized=True,
        js_api=api,
        background_color="#0b1020",
    )
    webview.start(debug=False)


if __name__ == "__main__":
    main()
