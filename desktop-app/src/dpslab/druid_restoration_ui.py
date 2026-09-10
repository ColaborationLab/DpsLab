"""Small manual screen for the one real Restoration recommendation flow."""

from __future__ import annotations

import json
import os
from pathlib import Path
import tempfile
import sys

from .addon_observation_acquisition import AddonObservationAcquisitionError, acquire_recent_live_analysis_export
from .druid_balance_recommendation import run_druid_balance_recommendation
from .druid_restoration_recommendation import DruidRestorationRecommendationError, run_druid_restoration_recommendation


def _bundled_simc() -> str:
    root = Path(getattr(sys, "_MEIPASS", ""))
    candidate = root / "simc" / "simc.exe"
    return str(candidate) if candidate.is_file() else ""


def _default_addon_path() -> str:
    program_files = os.environ.get("ProgramFiles(x86)")
    if not program_files:
        return ""
    candidate = Path(program_files) / "World of Warcraft" / "_retail_" / "Interface" / "AddOns" / "DpsLab"
    return str(candidate) if candidate.is_dir() else ""


def _settings_path() -> Path:
    local_app_data = os.environ.get("LOCALAPPDATA")
    if not local_app_data:
        return Path.home() / "AppData" / "Local" / "DpsLab" / "workspace_paths.json"
    return Path(local_app_data) / "DpsLab" / "workspace_paths.json"


def _remembered_paths(path: Path) -> tuple[str, str] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(value, dict) or set(value) != {"addon", "simc", "schema_version"}:
        return None
    if value["schema_version"] != "0.1":
        return None
    paths = (value["simc"], value["addon"])
    if not all(isinstance(item, str) and 1 <= len(item) <= 4096 for item in paths):
        return None
    return paths


def _save_paths(path: Path, simc: str, addon: str) -> None:
    if not all(isinstance(item, str) and 1 <= len(item) <= 4096 for item in (simc, addon)):
        raise ValueError("workspace_paths_invalid")
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as temporary:
        temporary.write(json.dumps({"schema_version": "0.1", "simc": simc, "addon": addon}, sort_keys=True))
        temporary.write("\n")
        temporary_name = temporary.name
    os.replace(temporary_name, path)


def _clear_paths(path: Path) -> None:
    path.unlink(missing_ok=True)


class TkDruidRecommendationWorkspace:
    """Detect one attended addon export and compare its two saved loadouts."""

    def __init__(self, root: Path, specialization: str, recommendation_runner: object) -> None:
        import tkinter as tk
        from tkinter import filedialog, ttk

        self._root = root
        self._settings = _settings_path()
        self._recommendation_runner = recommendation_runner
        self._filedialog = filedialog
        self._tk = tk
        self._window = tk.Tk()
        self._window.title(f"DpsLab — Comparación de {specialization}")
        self._window.geometry("760x560")
        self._window.minsize(620, 440)
        saved = _remembered_paths(self._settings)
        self._simc = tk.StringVar(value=saved[0] if saved else _bundled_simc())
        self._addon = tk.StringVar(value=saved[1] if saved else _default_addon_path())
        self._remember = tk.BooleanVar(value=saved is not None)
        self._export_text = ""
        self._build = tk.StringVar(value="Sin exportación detectada")
        self._status = tk.StringVar(value="En WoW usa /dpslab export app, confirma /reload y luego vuelve aquí.")
        frame = ttk.Frame(self._window, padding=18)
        frame.grid(sticky="nsew")
        self._window.columnconfigure(0, weight=1)
        self._window.rowconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        ttk.Label(frame, text=f"Comparación real — Druida {specialization}", font=("Segoe UI", 14, "bold")).grid(column=0, row=0, columnspan=3, sticky="w")
        ttk.Label(frame, text="SimulationCraft (simc.exe)").grid(column=0, row=1, pady=(14, 4), sticky="w")
        ttk.Entry(frame, textvariable=self._simc).grid(column=1, row=1, pady=(14, 4), sticky="ew")
        ttk.Button(frame, text="Elegir", command=self._choose_simc).grid(column=2, row=1, padx=(8, 0), pady=(14, 4))
        ttk.Label(frame, text="Carpeta del addon DpsLab").grid(column=0, row=2, pady=4, sticky="w")
        ttk.Entry(frame, textvariable=self._addon).grid(column=1, row=2, pady=4, sticky="ew")
        ttk.Button(frame, text="Elegir", command=self._choose_addon).grid(column=2, row=2, padx=(8, 0), pady=4)
        ttk.Checkbutton(frame, text="Recordar estas rutas en este equipo", variable=self._remember).grid(column=0, row=3, columnspan=3, pady=4, sticky="w")
        ttk.Label(frame, text="Builds detectadas").grid(column=0, row=5, pady=(12, 4), sticky="w")
        self._builds = ttk.Combobox(frame, textvariable=self._build, state="readonly")
        self._builds.grid(column=1, row=5, columnspan=2, pady=(12, 4), sticky="ew")
        ttk.Button(frame, text="Detectar exportación", command=self._detect).grid(column=0, row=6, pady=(8, 4), sticky="w")
        ttk.Button(frame, text="Ejecutar comparación real", command=self._run).grid(column=1, row=6, pady=(8, 4), sticky="w")
        ttk.Label(frame, textvariable=self._status, wraplength=700).grid(column=0, row=7, columnspan=3, sticky="w")
        if self._addon.get():
            self._detect()

    def _choose_simc(self) -> None:
        selected = self._filedialog.askopenfilename(title="Selecciona simc.exe", filetypes=[("SimulationCraft", "simc.exe"), ("Todos", "*")])
        if selected:
            self._simc.set(selected)

    def _choose_addon(self) -> None:
        selected = self._filedialog.askdirectory(title="Selecciona la carpeta DpsLab del addon")
        if selected:
            self._addon.set(selected)

    def _detect(self) -> None:
        try:
            addon = Path(self._addon.get()).resolve()
            retail = addon.parents[2]
            export = acquire_recent_live_analysis_export(retail)
            loadouts = export.snapshot.talent_loadouts
            if loadouts is None:
                raise ValueError("loadouts_unavailable")
        except (AddonObservationAcquisitionError, IndexError, OSError, ValueError):
            self._export_text = ""
            self._builds["values"] = ()
            self._build.set("Sin exportación detectada")
            self._status.set("No hay una exportación válida. En WoW usa /dpslab export app y confirma /reload.")
            return
        choices = (f"Activa ({loadouts.active_config_id})", f"Comparación ({loadouts.comparison_config_id})")
        self._export_text = export.text
        self._builds["values"] = choices
        self._build.set(choices[0])
        self._status.set("Exportación detectada. Revisa las dos builds y ejecuta la comparación.")

    def _run(self) -> None:
        self._status.set("Ejecutando las dos simulaciones reales…")
        self._window.update_idletasks()
        try:
            result = self._recommendation_runner(
                self._export_text,
                Path(self._simc.get()),
                Path(self._addon.get()),
                root=self._root,
            )
        except (DruidRestorationRecommendationError, OSError, ValueError) as exc:
            self._status.set(f"No se generó recomendación: {exc}")
            return
        try:
            if self._remember.get():
                _save_paths(self._settings, self._simc.get(), self._addon.get())
            else:
                _clear_paths(self._settings)
        except OSError:
            self._status.set(f"{result.message} No se pudieron recordar las rutas.")
            return
        self._status.set(f"{result.message} Ejecuta /reload y luego /dpslab result en WoW.")

    def run(self) -> None:
        self._window.mainloop()


class TkDruidRestorationWorkspace(TkDruidRecommendationWorkspace):
    def __init__(self, root: Path) -> None:
        super().__init__(root, "Restauración", run_druid_restoration_recommendation)


class TkDruidBalanceWorkspace(TkDruidRecommendationWorkspace):
    def __init__(self, root: Path) -> None:
        super().__init__(root, "Balance", run_druid_balance_recommendation)
