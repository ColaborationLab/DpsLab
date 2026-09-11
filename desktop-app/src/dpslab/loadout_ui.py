"""Manual class/spec-neutral desktop workspace for the player loadout flow."""
from __future__ import annotations

from pathlib import Path
from queue import Empty, Queue
from threading import Thread

from .addon_observation_acquisition import AddonObservationAcquisitionError, acquire_recent_live_analysis_export
from .druid_restoration_ui import _bundled_simc, _clear_paths, _default_addon_path, _remembered_paths, _save_paths, _settings_path
from .loadout_capabilities import capability_for
from .loadout_comparison_library import LoadoutComparisonLibraryError, list_cases, save_case
from .loadout_recommendation import LoadoutComparison, run_loadout_recommendation


class TkLoadoutWorkspace:
    def __init__(self, root: Path, recommendation_runner=run_loadout_recommendation) -> None:
        import tkinter as tk
        from tkinter import filedialog, ttk
        self._root, self._runner, self._filedialog = root, recommendation_runner, filedialog
        self._window = tk.Tk(); self._window.title("DpsLab — Comparación de loadouts"); self._window.geometry("780x590")
        self._window.columnconfigure(0, weight=1)
        saved = _remembered_paths(_settings_path()); bundled = _bundled_simc()
        self._uses_bundled = bool(bundled); self._simc = tk.StringVar(value=bundled or (saved[0] if saved and saved[0] != "bundled" else "")); self._addon = tk.StringVar(value=saved[1] if saved else _default_addon_path()); self._remember = tk.BooleanVar(value=saved is not None)
        self._title = tk.StringVar(value="Comparación de loadouts"); self._status = tk.StringVar(value="En WoW usa /dpslab export app, confirma /reload y vuelve aquí."); self._imports = tk.StringVar(); self._case_title = tk.StringVar(value="Comparación de loadouts")
        self._export = ""; self._ids: tuple[int, ...] = (); self._names: dict[int, str] = {}; self._running = False; self._comparison = None; self._cases = ()
        frame = ttk.Frame(self._window, padding=18); frame.grid(sticky="nsew"); frame.columnconfigure(1, weight=1)
        ttk.Label(frame, textvariable=self._title, font=("Segoe UI", 14, "bold")).grid(column=0, row=0, columnspan=3, sticky="w")
        ttk.Label(frame, text="SimulationCraft").grid(column=0, row=1, pady=(14, 4), sticky="w")
        if self._uses_bundled: ttk.Label(frame, text="Incluido con DpsLab").grid(column=1, row=1, columnspan=2, sticky="w")
        else:
            ttk.Entry(frame, textvariable=self._simc).grid(column=1, row=1, sticky="ew")
            ttk.Button(frame, text="Elegir", command=self._choose_simc).grid(column=2, row=1, padx=(8, 0))
        ttk.Label(frame, text="Carpeta del addon DpsLab").grid(column=0, row=2, pady=4, sticky="w"); ttk.Entry(frame, textvariable=self._addon).grid(column=1, row=2, sticky="ew"); ttk.Button(frame, text="Elegir", command=self._choose_addon).grid(column=2, row=2, padx=(8, 0))
        ttk.Checkbutton(frame, text="Recordar estas rutas en este equipo", variable=self._remember).grid(column=0, row=3, columnspan=3, sticky="w")
        ttk.Label(frame, text="Builds detectadas").grid(column=0, row=4, pady=(12, 4), sticky="w"); self._builds = tk.Listbox(frame, selectmode="extended", height=6, exportselection=False); self._builds.grid(column=1, row=4, columnspan=2, sticky="ew")
        ttk.Label(frame, text="Importaciones (Nombre|cadena; ...)").grid(column=0, row=5, pady=4, sticky="w"); ttk.Entry(frame, textvariable=self._imports).grid(column=1, row=5, columnspan=2, sticky="ew")
        ttk.Label(frame, text="Nombre del caso").grid(column=0, row=6, pady=4, sticky="w"); ttk.Entry(frame, textvariable=self._case_title).grid(column=1, row=6, sticky="ew"); ttk.Button(frame, text="Guardar caso", command=self._save_case).grid(column=2, row=6, padx=(8, 0))
        self._details = tk.Text(frame, height=7, wrap="word", state="disabled"); self._details.grid(column=1, row=7, columnspan=2, pady=(6, 0), sticky="ew")
        self._progress = ttk.Progressbar(frame, mode="indeterminate"); self._progress.grid(column=1, row=8, columnspan=2, sticky="ew")
        ttk.Button(frame, text="Detectar exportación", command=self._detect).grid(column=0, row=9, pady=(8, 4), sticky="w"); self._run_button = ttk.Button(frame, text="Ejecutar comparación real", command=self._run); self._run_button.grid(column=1, row=9, pady=(8, 4), sticky="w"); ttk.Button(frame, text="Limpiar interfaz", command=self._clear_workspace).grid(column=2, row=9, padx=(8, 0), pady=(8, 4), sticky="e")
        ttk.Label(frame, textvariable=self._status, wraplength=720).grid(column=0, row=10, columnspan=3, sticky="w")
        if self._addon.get(): self._detect()

    def _choose_simc(self):
        value = self._filedialog.askopenfilename(title="Selecciona simc.exe", filetypes=[("SimulationCraft", "simc.exe"), ("Todos", "*")])
        if value: self._simc.set(value)

    def _choose_addon(self):
        value = self._filedialog.askdirectory(title="Selecciona la carpeta DpsLab del addon")
        if value: self._addon.set(value)

    def _clear_workspace(self):
        if self._running:
            self._status.set("Espera a que termine la simulación antes de limpiar la interfaz.")
            return
        self._export = ""; self._ids = (); self._names = {}; self._comparison = None
        self._imports.set(""); self._case_title.set("Comparación de loadouts"); self._title.set("Comparación de loadouts")
        self._builds.delete(0, "end")
        self._details.configure(state="normal"); self._details.delete("1.0", "end"); self._details.configure(state="disabled")
        self._status.set("Interfaz limpia. Las rutas se conservan; detecta una nueva exportación cuando quieras.")

    def _detect(self):
        try:
            addon = Path(self._addon.get()).resolve(); export = acquire_recent_live_analysis_export(addon.parents[2]); capability = capability_for(export.snapshot.class_id, export.snapshot.specialization_id, export.snapshot.role)
            if capability is None or not export.snapshot.balance_talent_loadouts: raise ValueError
        except (AddonObservationAcquisitionError, IndexError, OSError, ValueError):
            self._export = ""; self._ids = (); self._names = {}; self._builds.delete(0, "end"); self._status.set("No hay una exportación compatible. En WoW usa /dpslab export app y confirma /reload."); return
        self._export = export.text; self._ids = tuple(item.config_id for item in export.snapshot.balance_talent_loadouts); self._names = {item.config_id: item.name or f"Loadout {item.config_id}" for item in export.snapshot.balance_talent_loadouts}; self._title.set(f"DpsLab — {capability.label}"); self._builds.delete(0, "end")
        for item in export.snapshot.balance_talent_loadouts: self._builds.insert("end", item.name or f"Loadout {item.config_id}")
        self._builds.select_set(0, min(3, len(self._ids) - 1)); self._status.set("Exportación reciente detectada. Selecciona entre una y cuatro builds del mismo personaje y especialización.")

    def _imports_value(self):
        values = tuple(item.strip() for item in self._imports.get().split(";") if item.strip()); result = []
        for item in values:
            name, separator, talent = item.partition("|")
            if not separator or not name.strip() or not talent.strip(): raise ValueError
            result.append((name.strip(), talent.strip()))
        return tuple(result)

    def _run(self):
        if self._running or not self._export: return
        try:
            selected = tuple(self._ids[index] for index in self._builds.curselection()); imported = self._imports_value()
            if not 1 <= len(selected) + len(imported) <= 4: raise ValueError
        except (IndexError, ValueError): self._status.set("Selecciona entre una y cuatro builds; cada importación usa Nombre|cadena."); return
        self._names.update({-index: name for index, (name, _talent) in enumerate(imported, 1)})
        simc_path, addon_path = Path(self._simc.get()), Path(self._addon.get())
        self._running = True; self._run_button.state(["disabled"]); self._progress.start(12); self._status.set("Ejecutando simulaciones de la misma métrica (DPS)…")
        outcomes: Queue = Queue(maxsize=1)
        def execute():
            try: outcomes.put((self._runner(self._export, simc_path, addon_path, root=self._root, selected_config_ids=selected, imported_loadouts=imported), None))
            except Exception as exc: outcomes.put((None, exc))
        Thread(target=execute, daemon=True).start(); self._wait(outcomes)

    def _wait(self, outcomes):
        try: result, error = outcomes.get_nowait()
        except Empty: self._window.after(50, self._wait, outcomes); return
        self._running = False; self._run_button.state(["!disabled"]); self._progress.stop()
        if error is not None: self._status.set(f"No se generó comparación: {error}"); return
        self._comparison = result; self._render(result)
        try:
            if self._remember.get(): _save_paths(_settings_path(), "bundled" if self._uses_bundled else self._simc.get(), self._addon.get())
            else: _clear_paths(_settings_path())
        except OSError: pass
        self._status.set(f"{result.message} Ejecuta /reload y luego /dpslab result en WoW.")

    def _render(self, result: LoadoutComparison):
        self._details.configure(state="normal"); self._details.delete("1.0", "end"); self._details.insert("1.0", "\n".join(f"{self._names.get(identifier, f'Loadout {identifier}')}: {score:.0f} {result.metric}" for identifier, score in result.loadouts)); self._details.configure(state="disabled")

    def _save_case(self):
        if self._comparison is None: self._status.set("Ejecuta una comparación antes de guardar el caso."); return
        try: save_case(self._root, self._case_title.get(), self._export, self._comparison)
        except LoadoutComparisonLibraryError: self._status.set("No se pudo guardar el caso."); return
        self._status.set("Caso guardado localmente para esta clase y especialización.")

    def run(self): self._window.mainloop()
