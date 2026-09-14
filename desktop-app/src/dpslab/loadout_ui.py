"""Manual class/spec-neutral desktop workspace for the player loadout flow."""
from __future__ import annotations

from pathlib import Path
from queue import Empty, Queue
from threading import Thread
from dataclasses import replace

from .addon_observation_acquisition import AddonObservationAcquisitionError, acquire_recent_live_analysis_export
from .druid_restoration_ui import _bundled_simc, _clear_paths, _default_addon_path, _remembered_paths, _save_paths, _settings_path
from .loadout_capabilities import capability_for
from .loadout_comparison_library import LoadoutComparisonLibraryError, list_cases, save_case
from .loadout_recommendation import LoadoutComparison, LoadoutRecommendationError, decode_weight_transfer, encode_weight_transfer, run_loadout_recommendation
from .addon_live_analysis_transport import parse_live_analysis_export
from .item_score_profiles import BuildScoreProfile, ItemScoreProfileError, create_character, profile_details, profile_export, profile_simulation_id, remove_builds, rename_profile, store_imported_build, store_simulation_results, store_weight, update_from_export
from .loadout_comparison_library import list_character_profiles, save_character_profiles
from .loadout_recommendation import write_item_score_profiles


def _simulation_selection(selected_ids, unavailable, character, specialization_id):
    """Separate live loadouts from saved imports without requiring a profile."""
    selected = tuple(value for value in selected_ids if value > 0 and value not in unavailable)
    imported_builds = () if character is None else tuple(
        build for build in dict(character.specs).get(specialization_id, ())
        if build.build_id in selected_ids and build.build_id < 0
    )
    return selected, imported_builds


class _ToolTip:
    """Small Tk-only help bubble; avoids a UI dependency for button explanations."""
    def __init__(self, widget, text: str) -> None:
        self._widget, self._text, self._tip = widget, text, None
        widget.bind("<Enter>", self._show, add="+")
        widget.bind("<Leave>", self._hide, add="+")

    def _show(self, _event=None) -> None:
        if self._tip is not None:
            return
        import tkinter as tk
        self._tip = tk.Toplevel(self._widget); self._tip.wm_overrideredirect(True)
        self._tip.wm_geometry(f"+{self._widget.winfo_rootx() + 12}+{self._widget.winfo_rooty() + self._widget.winfo_height() + 4}")
        tk.Label(self._tip, text=self._text, justify="left", relief="solid", borderwidth=1, padx=6, pady=4).pack()

    def _hide(self, _event=None) -> None:
        if self._tip is not None:
            self._tip.destroy(); self._tip = None


class TkLoadoutWorkspace:
    def __init__(self, root: Path, recommendation_runner=run_loadout_recommendation) -> None:
        import tkinter as tk
        from tkinter import filedialog, messagebox, ttk
        self._root, self._runner, self._filedialog, self._messagebox = root, recommendation_runner, filedialog, messagebox
        self._window = tk.Tk(); self._window.title("DpsLab — Comparación de loadouts"); self._window.geometry("780x650")
        self._window.columnconfigure(0, weight=1)
        saved = _remembered_paths(_settings_path()); bundled = _bundled_simc()
        self._uses_bundled = bool(bundled); self._simc = tk.StringVar(value=bundled or (saved[0] if saved and saved[0] != "bundled" else "")); self._addon = tk.StringVar(value=saved[1] if saved else _default_addon_path()); self._remember = tk.BooleanVar(value=saved is not None)
        self._title = tk.StringVar(value="Comparación de loadouts"); self._status = tk.StringVar(value="En WoW usa /dpslab export app, confirma /reload y vuelve aquí."); self._imports = tk.StringVar(); self._case_title = tk.StringVar(value="Comparación de loadouts"); self._character_name = tk.StringVar(value="Personaje local"); self._realm = tk.StringVar(value="Reino local"); self._profile_name = tk.StringVar()
        self._export = ""; self._ids: tuple[int, ...] = (); self._build_ids: tuple[int, ...] = (); self._names: dict[int, str] = {}; self._unavailable: dict[int, str] = {}; self._running = False; self._comparison = None; self._cases = (); self._character = None; self._profile_ids = (); self._import_targets: tuple[int, ...] = (); self._saved_id_map: dict[int, int] = {}; self._saved_profile_mode = False; self._skipped = ""
        frame = ttk.Frame(self._window, padding=18); frame.grid(sticky="nsew"); frame.columnconfigure(1, weight=1)
        ttk.Label(frame, textvariable=self._title, font=("Segoe UI", 14, "bold")).grid(column=0, row=0, columnspan=3, sticky="w")
        ttk.Label(frame, text="SimulationCraft").grid(column=0, row=1, pady=(14, 4), sticky="w")
        if self._uses_bundled: ttk.Label(frame, text="Incluido con DpsLab").grid(column=1, row=1, columnspan=2, sticky="w")
        else:
            ttk.Entry(frame, textvariable=self._simc).grid(column=1, row=1, sticky="ew")
            ttk.Button(frame, text="Elegir", command=self._choose_simc).grid(column=2, row=1, padx=(8, 0))
        ttk.Label(frame, text="Carpeta del addon DpsLab").grid(column=0, row=2, pady=4, sticky="w"); ttk.Entry(frame, textvariable=self._addon).grid(column=1, row=2, sticky="ew"); ttk.Button(frame, text="Elegir", command=self._choose_addon).grid(column=2, row=2, padx=(8, 0))
        ttk.Label(frame, text="Personaje / reino detectados").grid(column=0, row=3, pady=4, sticky="w"); ttk.Entry(frame, textvariable=self._character_name).grid(column=1, row=3, sticky="ew"); ttk.Entry(frame, textvariable=self._realm, width=18).grid(column=2, row=3, padx=(8, 0), sticky="ew")
        ttk.Label(frame, text="Nombre del perfil").grid(column=0, row=4, pady=4, sticky="w"); ttk.Entry(frame, textvariable=self._profile_name).grid(column=1, row=4, sticky="ew"); self._save_profile_button = ttk.Button(frame, text="Guardar perfil", command=self._save_profile); self._save_profile_button.grid(column=2, row=4, padx=(8, 0)); _ToolTip(self._save_profile_button, "Guarda este perfil con sus specs y loadouts detectados. No ejecuta SimulationCraft.")
        ttk.Label(frame, text="Perfil guardado").grid(column=0, row=5, pady=4, sticky="w"); self._profiles = ttk.Combobox(frame, state="readonly"); self._profiles.grid(column=1, row=5, sticky="ew"); self._open_profile_button = ttk.Button(frame, text="Abrir", command=self._open_profile); self._open_profile_button.grid(column=2, row=5, padx=(8, 0)); _ToolTip(self._open_profile_button, "Abre el perfil y muestra sus especializaciones, loadouts, resultados y pesos guardados.")
        ttk.Checkbutton(frame, text="Recordar estas rutas en este equipo", variable=self._remember).grid(column=0, row=6, columnspan=2, sticky="w"); self._delete_profile_button = ttk.Button(frame, text="Eliminar perfil", command=self._delete_profile); self._delete_profile_button.grid(column=2, row=6, padx=(8, 0)); _ToolTip(self._delete_profile_button, "Elimina el perfil seleccionado y sus builds, resultados y pesos locales. No toca el personaje ni WoW.")
        ttk.Label(frame, text="Builds detectadas").grid(column=0, row=7, pady=(12, 4), sticky="w"); self._builds = tk.Listbox(frame, selectmode="extended", height=6, exportselection=False); self._builds.grid(column=1, row=7, sticky="ew"); self._remove_button = ttk.Button(frame, text="Eliminar builds", command=self._remove_selected_builds); self._remove_button.grid(column=2, row=7, padx=(8, 0), sticky="n"); _ToolTip(self._remove_button, "Quita solo las builds seleccionadas del perfil. No borra el personaje, sus otras specs ni casos.")
        ttk.Label(frame, text="Importaciones (Nombre|cadena o cadena; ...)").grid(column=0, row=8, pady=4, sticky="w"); ttk.Entry(frame, textvariable=self._imports).grid(column=1, row=8, sticky="ew"); self._save_import_button = ttk.Button(frame, text="Guardar build", command=self._save_imports); self._save_import_button.grid(column=2, row=8, padx=(8, 0)); _ToolTip(self._save_import_button, "Guarda la cadena importada como build del perfil sin ejecutar una simulación. Si omites Nombre|, usa el nombre del caso.")
        ttk.Label(frame, text="Nombre del caso").grid(column=0, row=9, pady=4, sticky="w"); ttk.Entry(frame, textvariable=self._case_title).grid(column=1, row=9, sticky="ew"); self._save_case_button = ttk.Button(frame, text="Guardar caso", command=self._save_case); self._save_case_button.grid(column=2, row=9, padx=(8, 0)); _ToolTip(self._save_case_button, "Guarda la comparación actual y sus resultados como un caso local. No modifica el perfil.")
        self._details = tk.Text(frame, height=7, wrap="word", state="disabled"); self._details.grid(column=1, row=10, columnspan=2, pady=(6, 0), sticky="ew")
        self._progress = ttk.Progressbar(frame, mode="indeterminate"); self._progress.grid(column=1, row=11, columnspan=2, sticky="ew")
        self._detect_button = ttk.Button(frame, text="Detectar exportación", command=self._detect); self._detect_button.grid(column=0, row=12, pady=(8, 4), sticky="w"); _ToolTip(self._detect_button, "Lee la última exportación confirmada por el addon desde SavedVariables locales.")
        self._run_button = ttk.Button(frame, text="Ejecutar comparación real", command=self._run); self._run_button.grid(column=1, row=12, pady=(8, 4), sticky="w"); _ToolTip(self._run_button, "Ejecuta SimulationCraft para las builds seleccionadas y guarda los pesos obtenidos.")
        self._export_scores_button = ttk.Button(frame, text="Exportar pesos elegidos", command=self._export_chosen_scores); self._export_scores_button.grid(column=2, row=12, padx=(8, 0), pady=(8, 4), sticky="e"); _ToolTip(self._export_scores_button, "Envía al addon solo los pesos de las builds simuladas que selecciones. No elige automáticamente la build ganadora.")
        self._paste_export_button = ttk.Button(frame, text="Pegar exportación", command=self._paste_export); self._paste_export_button.grid(column=0, row=13, pady=4, sticky="w"); _ToolTip(self._paste_export_button, "Lee del portapapeles la exportación manual mostrada por /dpslab export analysis.")
        self._copy_weights_button = ttk.Button(frame, text="Copiar pesos", command=self._copy_weights); self._copy_weights_button.grid(column=1, row=13, pady=4, sticky="w"); _ToolTip(self._copy_weights_button, "Copia los pesos simulados de una única build seleccionada para importarlos manualmente en el addon.")
        self._paste_weights_button = ttk.Button(frame, text="Pegar pesos", command=self._paste_weights); self._paste_weights_button.grid(column=2, row=13, pady=4, sticky="e"); _ToolTip(self._paste_weights_button, "Guarda en la build seleccionada una cadena de pesos editada en el addon.")
        self._clear_button = ttk.Button(frame, text="Limpiar interfaz", command=self._clear_workspace); self._clear_button.grid(column=2, row=14, padx=(8, 0), pady=(2, 4), sticky="e"); _ToolTip(self._clear_button, "Limpia la comparación actual sin borrar perfiles, casos ni rutas recordadas.")
        ttk.Label(frame, textvariable=self._status, wraplength=720).grid(column=0, row=15, columnspan=3, sticky="w")
        self._refresh_profiles()
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
        if not self._messagebox.askyesno("Limpiar interfaz", "Se borrarán los datos no guardados de esta pantalla: personaje, reino, nombre de perfil, builds seleccionadas, importaciones y resultados.\n\nLos perfiles guardados y las rutas configuradas se conservarán. ¿Continuar?", parent=self._window):
            return
        self._export = ""; self._ids = (); self._build_ids = (); self._names = {}; self._unavailable = {}; self._saved_id_map = {}; self._saved_profile_mode = False; self._comparison = None
        self._character = None; self._imports.set(""); self._case_title.set("Comparación de loadouts"); self._character_name.set(""); self._realm.set(""); self._profile_name.set(""); self._title.set("Comparación de loadouts")
        self._profiles.set("")
        self._builds.delete(0, "end")
        self._details.configure(state="normal"); self._details.delete("1.0", "end"); self._details.configure(state="disabled")
        self._status.set("Interfaz limpia. Los perfiles guardados y las rutas se conservan; detecta una nueva exportación cuando quieras.")

    def _refresh_profiles(self):
        try: profiles = list_character_profiles(self._root)
        except ItemScoreProfileError: profiles = ()
        self._profile_ids = tuple(item.character_id for item in profiles)
        self._profiles["values"] = tuple(f"{item.profile_name or item.name} — {item.name} ({item.realm}) [{item.character_id[-6:]}]" for item in profiles)
        if self._character is not None:
            try: self._profiles.current(self._profile_ids.index(self._character.character_id))
            except ValueError: pass

    def _open_profile(self):
        index = self._profiles.current()
        if index < 0 or index >= len(self._profile_ids):
            self._status.set("Selecciona un perfil guardado para abrirlo."); return
        try: self._character = next(item for item in list_character_profiles(self._root) if item.character_id == self._profile_ids[index])
        except (ItemScoreProfileError, StopIteration): self._status.set("No se pudo abrir el perfil guardado."); return
        self._character_name.set(self._character.name); self._realm.set(self._character.realm); self._profile_name.set(self._character.profile_name or f"{self._character.name} — {self._character.realm}"); self._title.set(f"DpsLab — {self._character.name} ({self._character.realm})")
        try:
            snapshot = parse_live_analysis_export(self._export)
            matching_export = (snapshot.character_name, snapshot.realm_name, snapshot.class_id) == (self._character.name, self._character.realm, self._character.class_id)
        except ValueError:
            matching_export = False
        saved_context = False
        if matching_export:
            self._saved_id_map = {}; self._saved_profile_mode = False
            self._show_builds(snapshot)
        else:
            try:
                specialization_id = self._character.specs[0][0]
                self._export = profile_export(self._character, specialization_id)
                self._saved_id_map = {profile_simulation_id(build.build_id): build.build_id for build in dict(self._character.specs)[specialization_id] if build.build_id < 0}; self._saved_profile_mode = True
                self._show_builds(parse_live_analysis_export(self._export)); saved_context = True
            except (IndexError, ItemScoreProfileError, ValueError):
                self._export = ""; self._show_saved_profile_builds()
        self._details.configure(state="normal"); self._details.delete("1.0", "end"); self._details.insert("1.0", "\n".join(profile_details(self._character))); self._details.configure(state="disabled")
        self._status.set("Perfil abierto: selecciona builds y simula con su equipo guardado." if matching_export or saved_context else "Perfil antiguo abierto: conserva equipo y builds, pero no guardó nivel y raza. Expórtalo una vez para actualizarlo antes de simular.")

    def _delete_profile(self):
        index = self._profiles.current()
        if index < 0 or index >= len(self._profile_ids):
            self._status.set("Selecciona un perfil guardado para eliminar."); return
        identifier = self._profile_ids[index]
        try:
            save_character_profiles(self._root, tuple(item for item in list_character_profiles(self._root) if item.character_id != identifier))
        except (ItemScoreProfileError, OSError):
            self._status.set("No se pudo eliminar el perfil seleccionado."); return
        if self._character is not None and self._character.character_id == identifier:
            self._character = None; self._export = ""; self._build_ids = (); self._names = {}; self._builds.delete(0, "end")
            self._details.configure(state="normal"); self._details.delete("1.0", "end"); self._details.configure(state="disabled")
        self._refresh_profiles(); self._status.set("Perfil eliminado localmente. WoW y los demás perfiles no se modificaron.")

    def _show_saved_profile_builds(self):
        values = tuple((specialization_id, build) for specialization_id, builds in self._character.specs for build in builds)
        self._build_ids = tuple(build.build_id for _, build in values); self._names = {build.build_id: build.name for _, build in values}; self._unavailable = {}
        self._builds.delete(0, "end")
        for specialization_id, build in values:
            self._builds.insert("end", f"Spec {specialization_id} — {build.name}")

    def _prepare_profile(self, snapshot):
        name, realm = self._character_name.get().strip(), self._realm.get().strip()
        profile_name = self._profile_name.get().strip() or f"{name} — {realm}"
        if self._character is None or (self._character.name, self._character.realm, self._character.class_id) != (name, realm, snapshot.class_id):
            matches = [item for item in list_character_profiles(self._root) if (item.name, item.realm, item.class_id, item.profile_name) == (name, realm, snapshot.class_id, profile_name)]
            self._character = matches[0] if len(matches) == 1 else create_character(name, realm, snapshot.class_id, profile_name)
        self._character = rename_profile(update_from_export(self._character, snapshot), profile_name)
        return self._character

    def _persist_profile(self):
        stored = tuple(item for item in list_character_profiles(self._root) if item.character_id != self._character.character_id) + (self._character,)
        save_character_profiles(self._root, stored); self._refresh_profiles()

    def _save_profile(self):
        if not self._export:
            self._status.set("Detecta una exportación antes de guardar un perfil."); return
        try:
            snapshot = parse_live_analysis_export(self._export); self._prepare_profile(snapshot); self._persist_profile()
        except (ItemScoreProfileError, OSError, ValueError):
            self._status.set("No se pudo guardar el perfil: revisa personaje, reino y nombre del perfil."); return
        specs = len(self._character.specs); builds = sum(len(values) for _, values in self._character.specs)
        self._status.set(f"Perfil '{self._character.profile_name}' guardado: {specs} especialización(es) y {builds} loadout(s).")

    def _show_builds(self, snapshot):
        builds = () if self._saved_profile_mode else (dict(self._character.specs).get(snapshot.specialization_id, ()) if self._character is not None else ())
        if not builds:
            builds = tuple(BuildScoreProfile(item.config_id, item.name or f"Loadout {item.config_id}", item.talent_string) for item in snapshot.balance_talent_loadouts)
        live = {item.config_id: item for item in snapshot.balance_talent_loadouts}
        self._build_ids = tuple(build.build_id for build in builds); self._names = {build.build_id: build.name for build in builds}
        self._unavailable = {item.config_id: item.unavailable_reason for item in live.values() if not item.simulatable}
        self._builds.delete(0, "end")
        for build in builds:
            reason = self._unavailable.get(build.build_id)
            suffix = ""
            if reason == "talents_unassigned":
                suffix = " — talentos sin asignar"
            elif reason:
                suffix = " — estado de talentos no disponible"
            self._builds.insert("end", build.name + suffix)

    def _save_imports(self):
        if not self._export:
            self._status.set("Detecta una exportación antes de guardar una build importada."); return
        try:
            snapshot = parse_live_analysis_export(self._export); imported = self._imports_value()
            if not imported: raise ValueError
            self._prepare_profile(snapshot)
            for name, talent in imported: self._character = store_imported_build(self._character, snapshot.specialization_id, name, talent)
            self._persist_profile(); self._imports.set(""); self._show_builds(snapshot)
        except (ItemScoreProfileError, OSError, ValueError):
            self._status.set("No se pudo guardar la cadena: usa una cadena de talentos válida y un perfil detectado."); return
        self._status.set(f"{len(imported)} build(s) importada(s) y guardada(s) en el perfil; puedes simularlas por separado cuando quieras.")

    def _remove_selected_builds(self):
        if not self._export:
            self._status.set("Detecta una exportación y selecciona las builds que quieres eliminar."); return
        selected = tuple(self._build_ids[index] for index in self._builds.curselection())
        if not selected:
            self._status.set("Selecciona una o más builds para eliminarlas del perfil."); return
        try:
            snapshot = parse_live_analysis_export(self._export); self._prepare_profile(snapshot)
            self._character = remove_builds(self._character, snapshot.specialization_id, selected); self._persist_profile(); self._show_builds(snapshot)
        except (ItemScoreProfileError, OSError, ValueError):
            self._status.set("No se pudieron eliminar las builds seleccionadas."); return
        self._status.set(f"{len(selected)} build(s) eliminada(s) del perfil. Las demás specs y el personaje se conservaron.")

    def _show_export(self, text):
        snapshot = parse_live_analysis_export(text); capability = capability_for(snapshot.class_id, snapshot.specialization_id, snapshot.role)
        if capability is None or not snapshot.balance_talent_loadouts: raise ValueError
        self._export = text; self._saved_id_map = {}; self._saved_profile_mode = False; self._ids = tuple(item.config_id for item in snapshot.balance_talent_loadouts); self._title.set(f"DpsLab — {capability.label}")
        if snapshot.character_name and snapshot.realm_name:
            self._character_name.set(snapshot.character_name); self._realm.set(snapshot.realm_name)
            if self._character is None: self._profile_name.set(f"{snapshot.character_name} — {snapshot.realm_name}")
        self._show_builds(snapshot)
        self._details.configure(state="normal"); self._details.delete("1.0", "end"); self._details.insert("1.0", f"Equipo exportado: {len(snapshot.equipped)} pieza(s).\nGuarda el perfil para conservar este equipo junto a sus specs y builds."); self._details.configure(state="disabled")
        if self._build_ids: self._builds.select_set(0, min(3, len(self._build_ids) - 1))

    def _paste_export(self):
        try: self._show_export(self._window.clipboard_get())
        except Exception:
            self._status.set("El portapapeles no contiene una exportación DpsLab válida."); return
        self._status.set("Exportación manual pegada. Selecciona de una a cuatro builds para simular.")

    def _detect(self):
        try:
            addon = Path(self._addon.get()).resolve(); export = acquire_recent_live_analysis_export(addon.parents[2]); self._show_export(export.text)
        except (AddonObservationAcquisitionError, IndexError, OSError, ValueError):
            self._export = ""; self._ids = (); self._names = {}; self._builds.delete(0, "end"); self._status.set("No hay una exportación compatible. En WoW usa /dpslab export app y confirma /reload."); return
        self._status.set("Exportación reciente detectada. Selecciona una a cuatro builds, o guarda una cadena importada para simularla sola.")

    def _imports_value(self):
        values = tuple(item.strip() for item in self._imports.get().split(";") if item.strip()); result = []
        for item in values:
            name, separator, talent = item.partition("|")
            if not separator: name, talent = (self._case_title.get().strip() if len(values) == 1 else f"Build importada {len(result) + 1}"), item
            if not name.strip() or not talent.strip(): raise ValueError
            result.append((name.strip(), talent.strip()))
        return tuple(result)

    def _run(self):
        if self._running:
            self._status.set("La simulación ya está en curso."); return
        if not self._export:
            self._status.set("Detecta una exportación antes de ejecutar una simulación."); return
        try:
            snapshot = parse_live_analysis_export(self._export)
            if snapshot.max_level and snapshot.level < snapshot.max_level:
                self._status.set(f"Este personaje es nivel {snapshot.level}; el máximo disponible es {snapshot.max_level}. No se simulará hasta alcanzar el nivel máximo."); return
            selected_ids = tuple(self._build_ids[index] for index in self._builds.curselection()); typed = self._imports_value()
            if typed:
                self._prepare_profile(snapshot)
                for name, talent in typed: self._character = store_imported_build(self._character, snapshot.specialization_id, name, talent)
                self._persist_profile(); self._show_builds(snapshot)
                selected_ids += tuple(build.build_id for build in dict(self._character.specs)[snapshot.specialization_id] if build.build_id < 0 and (build.name, build.talent_string) in typed and build.build_id not in selected_ids)
            blocked = tuple(value for value in selected_ids if value in self._unavailable)
            selected, imported_builds = _simulation_selection(
                selected_ids, self._unavailable, self._character, snapshot.specialization_id
            )
            imported = tuple((build.name, build.talent_string) for build in imported_builds)
            if blocked and not selected and not imported:
                self._status.set("No se simulará " + ", ".join(self._names[value] for value in blocked) + ": " + ("talentos sin asignar." if all(self._unavailable[value] == "talents_unassigned" for value in blocked) else "estado de talentos no disponible.")); return
            if not 1 <= len(selected) + len(imported) <= 4: raise ValueError
        except (IndexError, ItemScoreProfileError, ValueError): self._status.set("Selecciona entre una y cuatro builds; una cadena sin Nombre| usa el nombre del caso."); return
        self._skipped = "" if not blocked else "No se simuló " + ", ".join(self._names[value] for value in blocked) + ": " + ("talentos sin asignar. " if all(self._unavailable[value] == "talents_unassigned" for value in blocked) else "estado de talentos no disponible. ")
        self._import_targets = tuple(build.build_id for build in imported_builds); self._names.update({build.build_id: build.name for build in imported_builds})
        simc_path, addon_path = Path(self._simc.get()), Path(self._addon.get())
        self._running = True; self._run_button.state(["disabled"]); self._progress.start(12); self._status.set("Simulando con error objetivo de 0.1%; puede tardar varios minutos por build…")
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
        if self._import_targets:
            generated = tuple(identifier for identifier, _ in result.loadouts if identifier < 0); mapping = dict(zip(generated, self._import_targets))
            result = replace(result, loadouts=tuple((mapping.get(identifier, identifier), value) for identifier, value in result.loadouts), preferred_loadout=mapping.get(result.preferred_loadout, result.preferred_loadout), score_weights=tuple(replace(weight, build_id=mapping.get(weight.build_id, weight.build_id)) for weight in result.score_weights), relative_errors=tuple((mapping.get(identifier, identifier), value) for identifier, value in result.relative_errors), run_ids=tuple((mapping.get(identifier, identifier), value) for identifier, value in result.run_ids))
        if self._saved_id_map:
            self._names.update({original: self._names.get(generated, f"Build {original}") for generated, original in self._saved_id_map.items()})
            result = replace(result, loadouts=tuple((self._saved_id_map.get(identifier, identifier), value) for identifier, value in result.loadouts), preferred_loadout=self._saved_id_map.get(result.preferred_loadout, result.preferred_loadout), score_weights=tuple(replace(weight, build_id=self._saved_id_map.get(weight.build_id, weight.build_id)) for weight in result.score_weights), relative_errors=tuple((self._saved_id_map.get(identifier, identifier), value) for identifier, value in result.relative_errors), run_ids=tuple((self._saved_id_map.get(identifier, identifier), value) for identifier, value in result.run_ids))
        self._comparison = result; self._render(result); self._save_character_scores(result)
        try:
            if self._remember.get(): _save_paths(_settings_path(), "bundled" if self._uses_bundled else self._simc.get(), self._addon.get())
            else: _clear_paths(_settings_path())
        except OSError: pass
        self._status.set(f"{self._skipped}{result.message} Los resultados se guardaron localmente; selecciona una build simulada y usa ‘Exportar pesos elegidos’ para actualizar sus scores en WoW.")

    def _save_character_scores(self, result):
        try:
            snapshot = parse_live_analysis_export(self._export)
            if not self._saved_profile_mode:
                self._prepare_profile(snapshot)
            elif self._character is None:
                raise ItemScoreProfileError("character_profile_unavailable")
            for weight in result.score_weights: self._character = store_weight(self._character, weight)
            self._character = store_simulation_results(self._character, result.specialization_id, result.loadouts, result.score_weights, result.relative_errors, result.run_ids)
            self._persist_profile()
        except (ItemScoreProfileError, OSError, ValueError):
            self._status.set("La comparación se mostró, pero no se pudo guardar el perfil local.")

    def _export_chosen_scores(self):
        if self._comparison is None or self._character is None:
            self._status.set("Ejecuta una simulación y guarda el perfil antes de exportar pesos."); return
        selected = tuple(self._build_ids[index] for index in self._builds.curselection())
        available = {weight.build_id for weight in self._comparison.score_weights if weight.build_id is not None and weight.build_id > 0}
        chosen = tuple((self._comparison.specialization_id, build_id) for build_id in selected if build_id in available)
        if not chosen:
            self._status.set("Selecciona una build real que haya sido simulada; las cadenas externas no se pueden atribuir a un loadout de WoW."); return
        try:
            write_item_score_profiles(Path(self._addon.get()), self._character, chosen)
        except (OSError, ValueError):
            self._status.set("No se pudieron exportar los pesos al addon seleccionado."); return
        names = ", ".join(self._names.get(build_id, f"Loadout {build_id}") for _, build_id in chosen)
        self._status.set(f"Pesos exportados para {names}. En WoW usa /reload y revisa el tooltip del ítem.")

    def _one_selected_real_build(self):
        selected = tuple(self._build_ids[index] for index in self._builds.curselection())
        return selected[0] if len(selected) == 1 and selected[0] > 0 else None

    def _copy_weights(self):
        build_id = self._one_selected_real_build()
        if self._comparison is None or build_id is None:
            self._status.set("Selecciona una sola build real ya simulada para copiar sus pesos."); return
        weight = next((value for value in self._comparison.score_weights if value.build_id == build_id), None)
        if weight is None:
            self._status.set("La build seleccionada no tiene pesos simulados disponibles."); return
        value = encode_weight_transfer(weight, self._names.get(build_id, f"Loadout {build_id}"))
        self._window.clipboard_clear(); self._window.clipboard_append(value); self._window.update()
        self._status.set("Pesos copiados. En WoW abre /dpslab scores y usa ‘Importar pegado’.")

    def _paste_weights(self):
        build_id = self._one_selected_real_build()
        if not self._export or build_id is None:
            self._status.set("Selecciona una sola build real para recibir los pesos pegados."); return
        try:
            snapshot = parse_live_analysis_export(self._export)
            name, weight = decode_weight_transfer(self._window.clipboard_get(), class_id=snapshot.class_id, build_id=build_id)
            if weight.specialization_id != snapshot.specialization_id: raise LoadoutRecommendationError("weight_transfer_invalid")
            self._prepare_profile(snapshot); self._character = store_weight(self._character, weight); self._persist_profile()
        except Exception:
            self._status.set("El portapapeles no contiene pesos válidos para esta especialización."); return
        self._status.set(f"Pesos manuales '{name}' guardados en {self._names.get(build_id, build_id)}.")

    def _render(self, result: LoadoutComparison):
        errors = dict(result.relative_errors)
        lines = []
        for identifier, score in result.loadouts:
            error = errors.get(identifier)
            precision = "" if error is None else f" · error {error:.3g}%"
            lines.append(f"{self._names.get(identifier, f'Loadout {identifier}')}: {score:.0f} {result.metric}{precision}")
        self._details.configure(state="normal"); self._details.delete("1.0", "end"); self._details.insert("1.0", "\n".join(lines)); self._details.configure(state="disabled")

    def _save_case(self):
        if self._comparison is None: self._status.set("Ejecuta una comparación antes de guardar el caso."); return
        try: save_case(self._root, self._case_title.get(), self._export, self._comparison)
        except LoadoutComparisonLibraryError: self._status.set("No se pudo guardar el caso."); return
        self._status.set(f"Caso '{self._case_title.get().strip()}' guardado localmente: comparación y resultados. No modifica el perfil.")

    def run(self): self._window.mainloop()
