"""Small manual screen for the one real Restoration recommendation flow."""

from __future__ import annotations

import json
import os
from pathlib import Path
import tempfile
import sys

from .addon_observation_acquisition import AddonObservationAcquisitionError, acquire_recent_live_analysis_export
from .balance_comparison_library import BalanceComparisonLibraryError, list_cases, save_case
from .balance_stat_weights import BalanceStatWeights
from .addon_live_analysis_transport import LiveAnalysisTransportError, parse_live_analysis_export
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
        self._multi_select = specialization == "Balance"
        self._filedialog = filedialog
        self._tk = tk
        self._window = tk.Tk()
        self._window.title(f"DpsLab — Comparación de {specialization}")
        self._window.geometry("760x560")
        self._window.minsize(620, 440)
        saved = _remembered_paths(self._settings)
        bundled_simc = _bundled_simc()
        self._uses_bundled_simc = bool(bundled_simc)
        self._simc = tk.StringVar(value=bundled_simc or (saved[0] if saved else ""))
        self._addon = tk.StringVar(value=saved[1] if saved else _default_addon_path())
        self._remember = tk.BooleanVar(value=saved is not None)
        self._export_text = ""
        self._build_ids: tuple[int, ...] = ()
        self._imports = tk.StringVar(value="")
        self._case_title = tk.StringVar(value="Comparación Balance")
        self._last_comparison = None
        self._snapshot = None
        self._saved_cases = ()
        self._case_choice = tk.StringVar(value="")
        self._build = tk.StringVar(value="Sin exportación detectada")
        self._status = tk.StringVar(value="En WoW usa /dpslab export app, confirma /reload y luego vuelve aquí.")
        frame = ttk.Frame(self._window, padding=18)
        frame.grid(sticky="nsew")
        self._window.columnconfigure(0, weight=1)
        self._window.rowconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        ttk.Label(frame, text=f"Comparación real — Druida {specialization}", font=("Segoe UI", 14, "bold")).grid(column=0, row=0, columnspan=3, sticky="w")
        ttk.Label(frame, text="SimulationCraft").grid(column=0, row=1, pady=(14, 4), sticky="w")
        if self._uses_bundled_simc:
            ttk.Label(frame, text="Incluido con DpsLab").grid(column=1, row=1, columnspan=2, pady=(14, 4), sticky="w")
        else:
            ttk.Entry(frame, textvariable=self._simc).grid(column=1, row=1, pady=(14, 4), sticky="ew")
            ttk.Button(frame, text="Elegir", command=self._choose_simc).grid(column=2, row=1, padx=(8, 0), pady=(14, 4))
        ttk.Label(frame, text="Carpeta del addon DpsLab").grid(column=0, row=2, pady=4, sticky="w")
        ttk.Entry(frame, textvariable=self._addon).grid(column=1, row=2, pady=4, sticky="ew")
        ttk.Button(frame, text="Elegir", command=self._choose_addon).grid(column=2, row=2, padx=(8, 0), pady=4)
        ttk.Checkbutton(frame, text="Recordar estas rutas en este equipo", variable=self._remember).grid(column=0, row=3, columnspan=3, pady=4, sticky="w")
        ttk.Label(frame, text="Builds detectadas").grid(column=0, row=5, pady=(12, 4), sticky="w")
        if self._multi_select:
            self._builds = tk.Listbox(frame, selectmode="extended", height=4, exportselection=False)
            self._builds.grid(column=1, row=5, columnspan=2, pady=(12, 4), sticky="ew")
            ttk.Label(frame, text="Cadenas importadas (separa con ;)").grid(column=0, row=6, pady=(4, 0), sticky="w")
            ttk.Entry(frame, textvariable=self._imports).grid(column=1, row=6, columnspan=2, pady=(4, 0), sticky="ew")
            ttk.Label(frame, text="Nombre del caso").grid(column=0, row=7, pady=(4, 0), sticky="w")
            ttk.Entry(frame, textvariable=self._case_title).grid(column=1, row=7, pady=(4, 0), sticky="ew")
            ttk.Button(frame, text="Guardar caso", command=self._save_case).grid(column=2, row=7, padx=(8, 0), pady=(4, 0))
            ttk.Label(frame, text="Casos guardados").grid(column=0, row=8, pady=(4, 0), sticky="w")
            self._saved_case_choices = ttk.Combobox(frame, textvariable=self._case_choice, state="readonly")
            self._saved_case_choices.grid(column=1, row=8, pady=(4, 0), sticky="ew")
            ttk.Button(frame, text="Abrir caso", command=self._open_case).grid(column=2, row=8, padx=(8, 0), pady=(4, 0))
            ttk.Label(frame, text="Resultados y pesos").grid(column=0, row=9, pady=(8, 0), sticky="nw")
            self._details = tk.Text(frame, height=7, wrap="word", state="disabled")
            self._details.grid(column=1, row=9, columnspan=2, pady=(8, 0), sticky="ew")
        else:
            self._builds = ttk.Combobox(frame, textvariable=self._build, state="readonly")
            self._builds.grid(column=1, row=5, columnspan=2, pady=(12, 4), sticky="ew")
        action_row = 10 if self._multi_select else 6
        ttk.Button(frame, text="Detectar exportación", command=self._detect).grid(column=0, row=action_row, pady=(8, 4), sticky="w")
        ttk.Button(frame, text="Ejecutar comparación real", command=self._run).grid(column=1, row=action_row, pady=(8, 4), sticky="w")
        ttk.Label(frame, textvariable=self._status, wraplength=700).grid(column=0, row=action_row + 1, columnspan=3, sticky="w")
        if self._addon.get():
            self._detect()
        if self._multi_select:
            self._refresh_cases()

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
            loadouts = export.snapshot.balance_talent_loadouts if self._multi_select else export.snapshot.talent_loadouts
            if not loadouts:
                raise ValueError("loadouts_unavailable")
        except (AddonObservationAcquisitionError, IndexError, OSError, ValueError):
            self._export_text = ""
            self._snapshot = None
            if self._multi_select:
                self._builds.delete(0, "end")
            else:
                self._builds["values"] = ()
            self._build.set("Sin exportación detectada")
            self._status.set("No hay una exportación válida. En WoW usa /dpslab export app y confirma /reload.")
            return
        choices = tuple(f"Loadout {item.config_id}" for item in loadouts) if self._multi_select else (f"Activa ({loadouts.active_config_id})", f"Comparación ({loadouts.comparison_config_id})")
        self._export_text = export.text
        self._snapshot = export.snapshot
        if self._multi_select:
            self._build_ids = tuple(item.config_id for item in loadouts)
            self._builds.delete(0, "end")
            for choice in choices:
                self._builds.insert("end", choice)
            self._builds.select_set(0, "end")
        else:
            self._builds["values"] = choices
            self._build.set(choices[0])
        self._status.set("Exportación reciente detectada en los datos de WoW (no guardada por DpsLab). Selecciona de dos a cuatro builds y ejecuta la comparación.")

    def _run(self) -> None:
        selected = ()
        imported = ()
        if self._multi_select:
            selected = tuple(self._build_ids[index] for index in self._builds.curselection())
            imported = tuple(item.strip() for item in self._imports.get().split(";") if item.strip())
            if not 2 <= len(selected) + len(imported) <= 4:
                self._status.set("Selecciona entre dos y cuatro builds.")
                return
        self._status.set("Ejecutando las simulaciones reales…")
        self._window.update_idletasks()
        try:
            options = {"root": self._root}
            if self._multi_select:
                options["selected_config_ids"] = selected
                options["imported_talent_strings"] = imported
            result = self._recommendation_runner(self._export_text, Path(self._simc.get()), Path(self._addon.get()), **options)
        except (DruidRestorationRecommendationError, OSError, ValueError) as exc:
            self._status.set(f"No se generó recomendación: {exc}")
            return
        self._last_comparison = result
        if self._multi_select:
            self._render_balance_details(result)
        try:
            if self._remember.get():
                _save_paths(self._settings, "bundled" if self._uses_bundled_simc else self._simc.get(), self._addon.get())
            else:
                _clear_paths(self._settings)
        except OSError:
            self._status.set(f"{result.message} No se pudieron recordar las rutas.")
            return
        self._status.set(f"{result.message} Ejecuta /reload y luego /dpslab result en WoW.")

    def _render_balance_details(self, result) -> None:
        lines = [f"{'Importada ' + str(-identifier) if identifier < 0 else 'Loadout ' + str(identifier)}: {dps:.0f} DPS" for identifier, dps in result.loadouts]
        weights = result.stat_weights
        if weights is None:
            lines.append("SimC no entregó pesos válidos; Advisor mantiene la guía estándar.")
        else:
            lines.append(weights.pawn_compatible())
            if self._snapshot is not None:
                for item in self._snapshot.equipped:
                    if item.stats:
                        lines.append(f"Ítem {item.item_id}: {weights.score_item(item.stats):.1f} puntos")
        self._details.configure(state="normal")
        self._details.delete("1.0", "end")
        self._details.insert("1.0", "\n".join(lines))
        self._details.configure(state="disabled")

    def _save_case(self) -> None:
        if not self._multi_select or self._last_comparison is None:
            self._status.set("Ejecuta una comparación de Balance antes de guardar el caso.")
            return
        try:
            save_case(self._root, self._case_title.get(), self._export_text, self._last_comparison)
        except BalanceComparisonLibraryError:
            self._status.set("No se pudo guardar el caso.")
            return
        self._refresh_cases()
        self._status.set("Caso guardado. Podrás reabrirlo sin ejecutar SimC de nuevo.")

    def _refresh_cases(self) -> None:
        try:
            self._saved_cases = list_cases(self._root)
        except BalanceComparisonLibraryError:
            self._saved_cases = ()
        values = tuple(f"{case.title} ({case.saved_at})" for case in self._saved_cases)
        self._saved_case_choices["values"] = values
        if values:
            self._case_choice.set(values[0])

    def _open_case(self) -> None:
        try:
            index = self._saved_case_choices.current()
            case = self._saved_cases[index]
        except (IndexError, ValueError):
            self._status.set("Selecciona un caso guardado.")
            return
        self._export_text = case.export_text
        from .druid_balance_recommendation import DruidBalanceComparison
        weights = BalanceStatWeights(case.stat_weights) if case.stat_weights else None
        self._last_comparison = DruidBalanceComparison(case.message, case.loadouts, case.preferred_loadout, weights)
        try:
            self._snapshot = parse_live_analysis_export(case.export_text)
        except LiveAnalysisTransportError:
            self._snapshot = None
        self._build_ids = tuple(identifier for identifier, _ in case.loadouts if identifier > 0)
        self._builds.delete(0, "end")
        for identifier, dps in case.loadouts:
            label = f"Importada {-identifier}" if identifier < 0 else f"Loadout {identifier}"
            self._builds.insert("end", f"{label}: {dps:.0f} DPS")
        self._render_balance_details(self._last_comparison)
        self._status.set("Caso guardado abierto sin ejecutar SimC. Puedes revisar sus resultados o exportarlos.")

    def run(self) -> None:
        self._window.mainloop()


class TkDruidRestorationWorkspace(TkDruidRecommendationWorkspace):
    def __init__(self, root: Path) -> None:
        super().__init__(root, "Restauración", run_druid_restoration_recommendation)


class TkDruidBalanceWorkspace(TkDruidRecommendationWorkspace):
    def __init__(self, root: Path) -> None:
        super().__init__(root, "Balance", run_druid_balance_recommendation)
