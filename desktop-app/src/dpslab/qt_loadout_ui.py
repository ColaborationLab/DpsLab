"""Qt presentation for choosing and comparing up to four exported loadouts."""
from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path
from queue import Empty, Queue
from threading import Thread
from dataclasses import replace

from PySide6 import QtCore, QtGui, QtWidgets

from .addon_live_analysis_transport import parse_live_analysis_export
from .addon_observation_acquisition import AddonObservationAcquisitionError, acquire_recent_live_analysis_export
from .comparison_table import ComparisonTable, comparison_table
from .loadout_capabilities import capability_for
from .loadout_comparison_library import LoadoutComparisonLibraryError, list_character_profiles, save_case, save_character_profiles
from .loadout_recommendation import LoadoutComparison, LoadoutRecommendationError, decode_weight_transfer, encode_weight_transfer, run_loadout_recommendation, write_item_score_profiles
from .item_score_profiles import BuildScoreProfile, ItemScoreProfileError, create_character, profile_details, profile_export, profile_simulation_id, remove_builds, rename_profile, store_imported_build, store_simulation_results, store_weight, update_from_export
from .i18n import DEFAULT_LOCALE, SUPPORTED_LOCALES, messages, normalize_locale, tr


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
    root = Path(local_app_data) if local_app_data else Path.home() / "AppData" / "Local"
    return root / "DpsLab" / "workspace_paths.json"


def _remembered_paths(path: Path) -> tuple[str, str] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(value, dict) or set(value) != {"addon", "simc", "schema_version"} or value["schema_version"] != "0.1":
        return None
    paths = (value["simc"], value["addon"])
    return paths if all(isinstance(item, str) and 1 <= len(item) <= 4096 for item in paths) else None


def _save_paths(path: Path, simc: str, addon: str) -> None:
    if not all(isinstance(item, str) and 1 <= len(item) <= 4096 for item in (simc, addon)):
        raise ValueError("workspace_paths_invalid")
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as temporary:
        temporary.write(json.dumps({"schema_version": "0.1", "simc": simc, "addon": addon}, sort_keys=True) + "\n")
        temporary_name = temporary.name
    os.replace(temporary_name, path)


def _clear_paths(path: Path) -> None:
    path.unlink(missing_ok=True)


def _language_path() -> Path:
    root = os.environ.get("LOCALAPPDATA")
    return (Path(root) if root else Path.home() / "AppData" / "Local") / "DpsLab" / "language.json"


def _load_language(path: Path) -> str:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        raw = value.get("locale") if isinstance(value, dict) else "auto"
        return raw if raw == "auto" else normalize_locale(raw)
    except (OSError, ValueError):
        return "auto"


def _save_language(path: Path, locale: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as temporary:
        selected = "auto" if locale == "auto" else normalize_locale(locale)
        temporary.write(json.dumps({"schema_version": "0.1", "locale": selected}) + "\n")
        temporary_name = temporary.name
    os.replace(temporary_name, path)


def _simulation_selection(selected_ids, unavailable, character, specialization_id):
    selected = tuple(value for value in selected_ids if value > 0 and value not in unavailable)
    imported_builds = () if character is None else tuple(
        build for build in dict(character.specs).get(specialization_id, ())
        if build.build_id in selected_ids and build.build_id < 0
    )
    return selected, imported_builds


_STYLE = """
QMainWindow { background: #f7f7f7; }
QGroupBox { font-weight: 600; margin-top: 8px; padding-top: 10px; }
QTableWidget { background: white; gridline-color: #d8d8d8; }
QHeaderView::section { background: #5926b8; color: white; padding: 6px; font-weight: 600; }
QPushButton { padding: 6px 10px; }
"""


class ComparisonTableWidget(QtWidgets.QTableWidget):
    """Native table kept separate from acquisition and simulation services."""
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.NoSelection)
        self.setWordWrap(True)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)

    def show_table(self, table: ComparisonTable, statistic_label: str = "Estadística") -> None:
        self.clearContents()
        self.setColumnCount(1 + len(table.columns))
        self.setRowCount(len(table.rows))
        self.setHorizontalHeaderLabels((statistic_label,) + table.columns)
        accent = QtGui.QColor("#fff0c2")
        for row_index, row in enumerate(table.rows):
            label = QtWidgets.QTableWidgetItem(row.label)
            label.setToolTip(row.source)
            self.setItem(row_index, 0, label)
            for column_index, cell in enumerate(row.cells, start=1):
                text = cell.text if not cell.delta else f"{cell.text}\n({cell.delta})"
                item = QtWidgets.QTableWidgetItem(text)
                item.setToolTip(row.source)
                item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter)
                if row.highlighted:
                    item.setBackground(accent)
                self.setItem(row_index, column_index, item)
        self.resizeRowsToContents()


class QtLoadoutWorkspace(QtWidgets.QMainWindow):
    """Qt workspace that keeps the attended profile and loadout flow local."""
    def __init__(self, root: Path, recommendation_runner=run_loadout_recommendation) -> None:
        app = QtWidgets.QApplication.instance()
        self._owned_application = app is None
        self._application = app or QtWidgets.QApplication([])
        super().__init__()
        self._root, self._runner = root, recommendation_runner
        self._export = ""; self._snapshot = None; self._ids: tuple[int, ...] = (); self._build_ids: tuple[int, ...] = ()
        self._names: dict[int, str] = {}; self._unavailable: dict[int, str] = {}; self._running = False; self._comparison = None
        self._character = None; self._profile_ids: tuple[str, ...] = (); self._import_targets: tuple[int, ...] = (); self._saved_id_map: dict[int, int] = {}; self._saved_profile_mode = False; self._skipped = ""
        self._locale = _load_language(_language_path())
        self.setWindowTitle(self._t("app.title", "DpsLab — Comparación de loadouts"))
        self.setMinimumSize(780, 570)
        self.resize(1050, 730)
        self.setStyleSheet(_STYLE)
        self._build_ui()

    def _t(self, key: str, fallback: str) -> str:
        locale = None if self._locale == "auto" else self._locale
        return tr(key, locale, **({} if "{name}" not in fallback else {})) if key in messages(locale) else fallback

    def _set_language(self, locale: str) -> None:
        self._locale = locale if locale == "auto" else normalize_locale(locale)
        try:
            _save_language(_language_path(), self._locale)
        except OSError:
            pass
        self._set_status(self._t("language.changed", "Idioma actualizado. Abre de nuevo la ventana para aplicar todas las etiquetas."))

    def _build_ui(self) -> None:
        scroll = QtWidgets.QScrollArea(self); scroll.setWidgetResizable(True)
        body = QtWidgets.QWidget(scroll)
        scroll.setWidget(body)
        layout = QtWidgets.QVBoxLayout(body)
        layout.setContentsMargins(18, 18, 18, 18)
        self._title = QtWidgets.QLabel(self._t("app.title", "DpsLab — Comparación de loadouts"))
        self._title.setStyleSheet("font-size: 20px; font-weight: 700;")
        layout.addWidget(self._title)
        layout.addWidget(QtWidgets.QLabel(self._t("app.subtitle", "Compara de una a cuatro builds. Las filas N/D no se inventan cuando falta un dato.")))
        source = QtWidgets.QGroupBox(self._t("source.group", "Exportación del addon"))
        source_layout = QtWidgets.QGridLayout(source)
        saved = _remembered_paths(_settings_path()); bundled = _bundled_simc()
        self._simc_path = QtWidgets.QLineEdit(bundled or (saved[0] if saved and saved[0] != "bundled" else ""))
        self._addon_path = QtWidgets.QLineEdit(saved[1] if saved else _default_addon_path())
        self._remember = QtWidgets.QCheckBox(self._t("source.remember", "Recordar estas rutas en este equipo")); self._remember.setChecked(saved is not None)
        self._addon_path.setToolTip(self._t("source.addon_help", "Carpeta DpsLab dentro de Interface/AddOns."))
        self._simc_path.setToolTip(self._t("source.simc_help", "El paquete incluye SimulationCraft. Fuera del paquete, indica simc.exe."))
        source_layout.addWidget(QtWidgets.QLabel("SimulationCraft"), 0, 0)
        if bundled:
            source_layout.addWidget(QtWidgets.QLabel(self._t("simc.included", "Incluido con DpsLab")), 0, 1)
        else:
            source_layout.addWidget(self._simc_path, 0, 1)
            choose_simc = QtWidgets.QPushButton(self._t("common.choose", "Elegir")); choose_simc.clicked.connect(self._choose_simc); source_layout.addWidget(choose_simc, 0, 2)
        source_layout.addWidget(QtWidgets.QLabel(self._t("source.addon_path", "Carpeta del addon")), 1, 0)
        source_layout.addWidget(self._addon_path, 1, 1)
        choose_addon = QtWidgets.QPushButton(self._t("common.choose", "Elegir")); choose_addon.clicked.connect(self._choose_addon); source_layout.addWidget(choose_addon, 1, 2)
        source_layout.addWidget(self._remember, 2, 0, 1, 3)
        self._detect = QtWidgets.QPushButton(self._t("source.detect", "Detectar exportación"))
        self._detect.setToolTip(self._t("source.detect_help", "Lee la última exportación confirmada del addon."))
        self._detect.clicked.connect(self._detect_export)
        source_layout.addWidget(self._detect, 3, 0)
        paste_export = QtWidgets.QPushButton(self._t("source.paste", "Pegar exportación")); paste_export.setToolTip(self._t("source.paste_help", "Lee la exportación manual copiada desde el addon.")); paste_export.clicked.connect(self._paste_export); source_layout.addWidget(paste_export, 3, 1)
        source_layout.addWidget(QtWidgets.QLabel(self._t("language.label", "Idioma")), 4, 0)
        self._language_combo = QtWidgets.QComboBox()
        self._language_combo.addItem(self._t("language.auto", "Auto"), "auto")
        self._language_combo.addItem("ES", "es"); self._language_combo.addItem("EN", "en"); self._language_combo.addItem("PT-BR", "pt-BR")
        self._language_combo.setToolTip(self._t("language.help", "Selecciona Auto, español, inglés o portugués brasileño. Se guarda como preferencia local."))
        self._language_combo.setCurrentIndex(next((i for i in range(self._language_combo.count()) if self._language_combo.itemData(i) == self._locale), 0))
        self._language_combo.currentIndexChanged.connect(lambda i: self._set_language(self._language_combo.itemData(i)))
        source_layout.addWidget(self._language_combo, 4, 1)
        layout.addWidget(source)
        profiles = QtWidgets.QGroupBox(self._t("profile.group", "Personaje y perfil local"))
        profile_layout = QtWidgets.QGridLayout(profiles)
        self._character_name = QtWidgets.QLineEdit("Personaje local"); self._realm = QtWidgets.QLineEdit("Reino local"); self._profile_name = QtWidgets.QLineEdit()
        self._profiles = QtWidgets.QComboBox(); self._profiles.setToolTip(self._t("profile.help", "Perfiles locales guardados con equipo, builds, pesos y resultados."))
        save_profile = QtWidgets.QPushButton(self._t("profile.save", "Guardar perfil")); save_profile.setToolTip(self._t("profile.save_help", "Guarda personaje, equipo, especializaciones y loadouts detectados. No ejecuta SimulationCraft.")); save_profile.clicked.connect(self._save_profile)
        open_profile = QtWidgets.QPushButton(self._t("profile.open", "Abrir")); open_profile.setToolTip(self._t("profile.open_help", "Abre el perfil local seleccionado.")); open_profile.clicked.connect(self._open_profile)
        delete_profile = QtWidgets.QPushButton(self._t("profile.delete", "Eliminar perfil")); delete_profile.setToolTip(self._t("profile.delete_help", "Elimina solo el perfil local seleccionado; World of Warcraft no se modifica.")); delete_profile.clicked.connect(self._delete_profile)
        profile_layout.addWidget(QtWidgets.QLabel(self._t("profile.character", "Personaje")), 0, 0); profile_layout.addWidget(self._character_name, 0, 1); profile_layout.addWidget(QtWidgets.QLabel(self._t("profile.realm", "Reino")), 0, 2); profile_layout.addWidget(self._realm, 0, 3)
        profile_layout.addWidget(QtWidgets.QLabel(self._t("profile.name", "Nombre del perfil")), 1, 0); profile_layout.addWidget(self._profile_name, 1, 1, 1, 2); profile_layout.addWidget(save_profile, 1, 3)
        profile_layout.addWidget(QtWidgets.QLabel(self._t("profile.saved", "Perfil guardado")), 2, 0); profile_layout.addWidget(self._profiles, 2, 1, 1, 2); profile_layout.addWidget(open_profile, 2, 3); profile_layout.addWidget(delete_profile, 2, 4)
        layout.addWidget(profiles)
        middle = QtWidgets.QHBoxLayout()
        builds_group = QtWidgets.QGroupBox(self._t("builds.group", "Builds detectadas"))
        builds_layout = QtWidgets.QVBoxLayout(builds_group)
        self._builds = QtWidgets.QListWidget()
        self._builds.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
        self._builds.setToolTip(self._t("builds.help", "Selecciona una a cuatro builds. Las inválidas se muestran pero no se ejecutan."))
        builds_layout.addWidget(self._builds)
        remove_builds_button = QtWidgets.QPushButton(self._t("builds.remove", "Eliminar builds"))
        remove_builds_button.setToolTip(self._t("builds.remove_help", "Quita las builds seleccionadas del perfil local, sin borrar otras especializaciones ni loadouts de WoW."))
        remove_builds_button.clicked.connect(self._remove_selected_builds)
        builds_layout.addWidget(remove_builds_button)
        self._run = QtWidgets.QPushButton(self._t("simulation.run", "Ejecutar comparación real"))
        self._run.setToolTip(self._t("simulation.run_help", "Ejecuta SimulationCraft fuera del hilo de la ventana para las builds seleccionadas."))
        self._run.clicked.connect(self._start_run)
        builds_layout.addWidget(self._run)
        middle.addWidget(builds_group, 1)
        table_group = QtWidgets.QGroupBox(self._t("results.group", "Resultados y pesos"))
        table_layout = QtWidgets.QVBoxLayout(table_group)
        self._table = ComparisonTableWidget()
        table_layout.addWidget(self._table)
        middle.addWidget(table_group, 3)
        layout.addLayout(middle, 1)
        imports = QtWidgets.QGroupBox(self._t("imports.group", "Builds externas y casos"))
        imports_layout = QtWidgets.QGridLayout(imports)
        self._imports = QtWidgets.QLineEdit(); self._imports.setToolTip(self._t("imports.help", "Usa Nombre|cadena o cadena; separa builds con punto y coma."))
        save_import = QtWidgets.QPushButton(self._t("imports.save", "Guardar build")); save_import.setToolTip(self._t("imports.save_help", "Guarda una build externa en el perfil sin simularla.")); save_import.clicked.connect(self._save_imports)
        self._case_title = QtWidgets.QLineEdit("Comparación de loadouts")
        save_case_button = QtWidgets.QPushButton(self._t("case.save", "Guardar caso")); save_case_button.setToolTip(self._t("case.save_help", "Guarda la comparación y sus resultados localmente.")); save_case_button.clicked.connect(self._save_case)
        imports_layout.addWidget(QtWidgets.QLabel(self._t("imports.group", "Importaciones")), 0, 0); imports_layout.addWidget(self._imports, 0, 1); imports_layout.addWidget(save_import, 0, 2)
        imports_layout.addWidget(QtWidgets.QLabel(self._t("case.name", "Nombre del caso")), 1, 0); imports_layout.addWidget(self._case_title, 1, 1); imports_layout.addWidget(save_case_button, 1, 2)
        layout.addWidget(imports)
        actions = QtWidgets.QHBoxLayout()
        export_scores = QtWidgets.QPushButton(self._t("weights.export", "Exportar pesos elegidos")); export_scores.setToolTip(self._t("weights.export_help", "Envía al addon solo pesos de builds reales seleccionadas y simuladas.")); export_scores.clicked.connect(self._export_chosen_scores)
        copy_weights = QtWidgets.QPushButton(self._t("weights.copy", "Copiar pesos")); copy_weights.setToolTip(self._t("weights.copy_help", "Copia los pesos de una build real simulada.")); copy_weights.clicked.connect(self._copy_weights)
        paste_weights = QtWidgets.QPushButton(self._t("weights.paste", "Pegar pesos")); paste_weights.setToolTip(self._t("weights.paste_help", "Guarda una cadena de pesos copiada del addon en la build real seleccionada.")); paste_weights.clicked.connect(self._paste_weights)
        clear = QtWidgets.QPushButton(self._t("interface.clear", "Limpiar interfaz")); clear.setToolTip(self._t("interface.clear_help", "Limpia datos no guardados tras pedir confirmación; mantiene perfiles y rutas.")); clear.clicked.connect(self._clear_workspace)
        for button in (export_scores, copy_weights, paste_weights, clear): actions.addWidget(button)
        actions.addStretch(1); layout.addLayout(actions)
        self._progress = QtWidgets.QProgressBar()
        self._progress.setRange(0, 1)
        self._progress.setValue(0)
        self._progress.setTextVisible(False)
        layout.addWidget(self._progress)
        self._status = QtWidgets.QLabel(self._t("status.initial", "En WoW usa /dpslab export app, confirma /reload y vuelve aquí."))
        self._status.setWordWrap(True)
        layout.addWidget(self._status)
        self._details = QtWidgets.QPlainTextEdit(); self._details.setReadOnly(True); self._details.setMaximumBlockCount(200); self._details.setPlaceholderText(self._t("details.placeholder", "Aquí se muestran el equipo y los resultados del perfil.")); layout.addWidget(self._details)
        self.setCentralWidget(scroll)
        self._refresh_profiles()
        if self._addon_path.text(): self._detect_export()

    def _choose_simc(self) -> None:
        value, _ = QtWidgets.QFileDialog.getOpenFileName(self, self._t("dialog.choose_simc", "Selecciona simc.exe"), self._simc_path.text(), "SimulationCraft (simc.exe);;" + self._t("dialog.all_files", "Todos (*)"))
        if value: self._simc_path.setText(value)

    def _choose_addon(self) -> None:
        value = QtWidgets.QFileDialog.getExistingDirectory(self, self._t("dialog.choose_addon", "Selecciona la carpeta DpsLab del addon"), self._addon_path.text())
        if value: self._addon_path.setText(value)

    def _set_status(self, text: str) -> None:
        self._status.setText(text)

    def _refresh_profiles(self) -> None:
        try: profiles = list_character_profiles(self._root)
        except ItemScoreProfileError: profiles = ()
        self._profile_ids = tuple(item.character_id for item in profiles)
        self._profiles.clear()
        self._profiles.addItems(tuple(f"{item.profile_name or item.name} — {item.name} ({item.realm}) [{item.character_id[-6:]}]" for item in profiles))
        if self._character is not None and self._character.character_id in self._profile_ids:
            self._profiles.setCurrentIndex(self._profile_ids.index(self._character.character_id))

    def _detect_export(self) -> None:
        try:
            addon = Path(self._addon_path.text()).resolve()
            export = acquire_recent_live_analysis_export(addon.parents[2])
            self._show_export(export.text)
        except (AddonObservationAcquisitionError, IndexError, OSError, ValueError):
            self._export = ""; self._ids = (); self._names = {}; self._builds.clear()
            self._set_status(self._t("status.no_export", "No hay una exportación compatible."))
            return
        self._set_status(self._t("status.export_detected", "Exportación reciente detectada."))

    def _show_export(self, text: str) -> None:
        snapshot = parse_live_analysis_export(text)
        capability = capability_for(snapshot.class_id, snapshot.specialization_id, snapshot.role)
        if capability is None or not snapshot.balance_talent_loadouts:
            raise ValueError
        self._export, self._snapshot = text, snapshot; self._saved_id_map = {}; self._saved_profile_mode = False
        self._ids = tuple(item.config_id for item in snapshot.balance_talent_loadouts)
        self._title.setText(f"DpsLab — {capability.label}")
        if snapshot.character_name and snapshot.realm_name:
            self._character_name.setText(snapshot.character_name); self._realm.setText(snapshot.realm_name)
            if self._character is None: self._profile_name.setText(f"{snapshot.character_name} — {snapshot.realm_name}")
        self._show_builds(snapshot)
        self._details.setPlainText(tr("details.exported_gear", None if self._locale == "auto" else self._locale, count=len(snapshot.equipped)))

    def _paste_export(self) -> None:
        try: self._show_export(self._application.clipboard().text())
        except Exception:
            self._set_status(self._t("status.invalid_export", "El portapapeles no contiene una exportación DpsLab válida."))
            return
        self._set_status(self._t("status.manual_export", "Exportación manual pegada."))

    def _show_builds(self, snapshot) -> None:
        builds = () if self._saved_profile_mode else (dict(self._character.specs).get(snapshot.specialization_id, ()) if self._character is not None else ())
        if not builds:
            builds = tuple(BuildScoreProfile(item.config_id, item.name or f"Loadout {item.config_id}", item.talent_string) for item in snapshot.balance_talent_loadouts)
        live = {item.config_id: item for item in snapshot.balance_talent_loadouts}
        self._build_ids = tuple(build.build_id for build in builds); self._names = {build.build_id: build.name for build in builds}
        self._unavailable = {item.config_id: item.unavailable_reason for item in live.values() if not item.simulatable}
        self._builds.clear()
        for build in builds:
            reason = self._unavailable.get(build.build_id)
            text = build.name if not reason else self._t("builds.talents_unassigned", "{name} — talentos sin asignar").format(name=build.name) if reason == "talents_unassigned" else self._t("builds.talents_unknown", "{name} — estado de talentos no disponible").format(name=build.name)
            item = QtWidgets.QListWidgetItem(text)
            item.setData(QtCore.Qt.ItemDataRole.UserRole, build.build_id)
            if reason:
                item.setToolTip(self._t("builds.unavailable_help", "Esta build se conserva, pero no se simulará hasta completar sus talentos."))
                item.setFlags(item.flags() & ~QtCore.Qt.ItemFlag.ItemIsSelectable)
            self._builds.addItem(item)
        for index in range(min(4, self._builds.count())):
            if self._builds.item(index).flags() & QtCore.Qt.ItemFlag.ItemIsSelectable:
                self._builds.item(index).setSelected(True)

    def _show_saved_profile_builds(self) -> None:
        values = tuple((specialization_id, build) for specialization_id, builds in self._character.specs for build in builds)
        self._build_ids = tuple(build.build_id for _, build in values); self._names = {build.build_id: build.name for _, build in values}; self._unavailable = {}
        self._builds.clear()
        for specialization_id, build in values:
            item = QtWidgets.QListWidgetItem(f"Spec {specialization_id} — {build.name}")
            item.setData(QtCore.Qt.ItemDataRole.UserRole, build.build_id)
            self._builds.addItem(item)

    def _prepare_profile(self, snapshot):
        name, realm = self._character_name.text().strip(), self._realm.text().strip()
        profile_name = self._profile_name.text().strip() or f"{name} — {realm}"
        if self._character is None or (self._character.name, self._character.realm, self._character.class_id) != (name, realm, snapshot.class_id):
            matches = [item for item in list_character_profiles(self._root) if (item.name, item.realm, item.class_id, item.profile_name) == (name, realm, snapshot.class_id, profile_name)]
            self._character = matches[0] if len(matches) == 1 else create_character(name, realm, snapshot.class_id, profile_name)
        self._character = rename_profile(update_from_export(self._character, snapshot), profile_name)
        return self._character

    def _persist_profile(self) -> None:
        stored = tuple(item for item in list_character_profiles(self._root) if item.character_id != self._character.character_id) + (self._character,)
        save_character_profiles(self._root, stored); self._refresh_profiles()

    def _save_profile(self) -> None:
        if not self._export:
            self._set_status(self._t("status.need_export", "Detecta una exportación antes de continuar.")); return
        try:
            snapshot = parse_live_analysis_export(self._export); self._prepare_profile(snapshot); self._persist_profile()
        except (ItemScoreProfileError, OSError, ValueError):
            self._set_status("No se pudo guardar el perfil: revisa personaje, reino y nombre del perfil."); return
        specs = len(self._character.specs); builds = sum(len(values) for _, values in self._character.specs)
        self._set_status(tr("status.profile_saved", None if self._locale == "auto" else self._locale, name=self._character.profile_name, specs=specs, builds=builds))

    def _open_profile(self) -> None:
        index = self._profiles.currentIndex()
        if index < 0 or index >= len(self._profile_ids):
            self._set_status("Selecciona un perfil guardado para abrirlo."); return
        try: self._character = next(item for item in list_character_profiles(self._root) if item.character_id == self._profile_ids[index])
        except (ItemScoreProfileError, StopIteration):
            self._set_status("No se pudo abrir el perfil guardado."); return
        self._character_name.setText(self._character.name); self._realm.setText(self._character.realm); self._profile_name.setText(self._character.profile_name or f"{self._character.name} — {self._character.realm}"); self._title.setText(f"DpsLab — {self._character.name} ({self._character.realm})")
        try:
            snapshot = parse_live_analysis_export(self._export)
            matching_export = (snapshot.character_name, snapshot.realm_name, snapshot.class_id) == (self._character.name, self._character.realm, self._character.class_id)
        except ValueError: matching_export = False
        saved_context = False
        if matching_export:
            self._saved_id_map = {}; self._saved_profile_mode = False; self._show_builds(snapshot)
        else:
            try:
                specialization_id = self._character.specs[0][0]; self._export = profile_export(self._character, specialization_id)
                self._saved_id_map = {profile_simulation_id(build.build_id): build.build_id for build in dict(self._character.specs)[specialization_id] if build.build_id < 0}; self._saved_profile_mode = True
                self._snapshot = parse_live_analysis_export(self._export); self._show_builds(self._snapshot); saved_context = True
            except (IndexError, ItemScoreProfileError, ValueError):
                self._export = ""; self._snapshot = None; self._show_saved_profile_builds()
        self._details.setPlainText("\n".join(profile_details(self._character)))
        self._set_status(self._t("status.profile_opened", "Perfil abierto.") if matching_export or saved_context else self._t("status.profile_old", "Perfil antiguo abierto."))

    def _delete_profile(self) -> None:
        index = self._profiles.currentIndex()
        if index < 0 or index >= len(self._profile_ids):
            self._set_status("Selecciona un perfil guardado para eliminar."); return
        if QtWidgets.QMessageBox.question(self, self._t("dialog.delete_profile_title", "Eliminar perfil"), self._t("dialog.delete_profile_text", "¿Continuar?")) != QtWidgets.QMessageBox.StandardButton.Yes:
            return
        identifier = self._profile_ids[index]
        try: save_character_profiles(self._root, tuple(item for item in list_character_profiles(self._root) if item.character_id != identifier))
        except (ItemScoreProfileError, OSError):
            self._set_status("No se pudo eliminar el perfil seleccionado."); return
        if self._character is not None and self._character.character_id == identifier:
            self._character = None; self._export = ""; self._build_ids = (); self._names = {}; self._builds.clear(); self._details.clear()
        self._refresh_profiles(); self._set_status("Perfil eliminado localmente. WoW y los demás perfiles no se modificaron.")

    def _imports_value(self) -> tuple[tuple[str, str], ...]:
        values = tuple(item.strip() for item in self._imports.text().split(";") if item.strip()); result = []
        for item in values:
            name, separator, talent = item.partition("|")
            if not separator: name, talent = (self._case_title.text().strip() if len(values) == 1 else f"Build importada {len(result) + 1}"), item
            if not name.strip() or not talent.strip(): raise ValueError
            result.append((name.strip(), talent.strip()))
        return tuple(result)

    def _save_imports(self) -> None:
        if not self._export:
            self._set_status("Detecta una exportación antes de guardar una build importada."); return
        try:
            snapshot = parse_live_analysis_export(self._export); imported = self._imports_value()
            if not imported: raise ValueError
            self._prepare_profile(snapshot)
            for name, talent in imported: self._character = store_imported_build(self._character, snapshot.specialization_id, name, talent)
            self._persist_profile(); self._imports.clear(); self._show_builds(snapshot)
        except (ItemScoreProfileError, OSError, ValueError):
            self._set_status("No se pudo guardar la cadena: usa una cadena de talentos válida y un perfil detectado."); return
        self._set_status(f"{len(imported)} build(s) importada(s) y guardada(s) en el perfil; puedes simularlas por separado cuando quieras.")

    def _remove_selected_builds(self) -> None:
        if not self._export:
            self._set_status("Detecta una exportación y selecciona las builds que quieres eliminar."); return
        selected = self._selected_ids()
        if not selected:
            self._set_status("Selecciona una o más builds para eliminarlas del perfil."); return
        try:
            snapshot = parse_live_analysis_export(self._export); self._prepare_profile(snapshot)
            self._character = remove_builds(self._character, snapshot.specialization_id, selected); self._persist_profile(); self._show_builds(snapshot)
        except (ItemScoreProfileError, OSError, ValueError):
            self._set_status("No se pudieron eliminar las builds seleccionadas."); return
        self._set_status(f"{len(selected)} build(s) eliminada(s) del perfil. Las demás specs y el personaje se conservaron.")

    def _selected_ids(self) -> tuple[int, ...]:
        return tuple(item.data(QtCore.Qt.ItemDataRole.UserRole) for item in self._builds.selectedItems())

    def _start_run(self) -> None:
        if self._running:
            self._set_status("La simulación ya está en curso."); return
        if not self._export:
            self._set_status("Detecta una exportación antes de ejecutar una simulación."); return
        try:
            snapshot = parse_live_analysis_export(self._export)
            if snapshot.max_level and snapshot.level < snapshot.max_level:
                self._set_status(f"Este personaje es nivel {snapshot.level}; el máximo disponible es {snapshot.max_level}. No se simulará hasta alcanzar el nivel máximo."); return
            selected_ids = self._selected_ids(); typed = self._imports_value()
            if typed:
                self._prepare_profile(snapshot)
                for name, talent in typed: self._character = store_imported_build(self._character, snapshot.specialization_id, name, talent)
                self._persist_profile(); self._imports.clear(); self._show_builds(snapshot)
                selected_ids += tuple(build.build_id for build in dict(self._character.specs)[snapshot.specialization_id] if build.build_id < 0 and (build.name, build.talent_string) in typed and build.build_id not in selected_ids)
            blocked = tuple(value for value in selected_ids if value in self._unavailable)
            selected, imported_builds = _simulation_selection(selected_ids, self._unavailable, self._character, snapshot.specialization_id)
            imported = tuple((build.name, build.talent_string) for build in imported_builds)
            if blocked and not selected and not imported:
                self._set_status("No se simulará " + ", ".join(self._names[value] for value in blocked) + ": talentos sin asignar."); return
            if not 1 <= len(selected) + len(imported) <= 4: raise ValueError
        except (IndexError, ItemScoreProfileError, ValueError):
            self._set_status("Selecciona entre una y cuatro builds; una cadena sin Nombre| usa el nombre del caso."); return
        self._skipped = "" if not blocked else "No se simuló " + ", ".join(self._names[value] for value in blocked) + ": talentos sin asignar. "
        self._import_targets = tuple(build.build_id for build in imported_builds); self._names.update({build.build_id: build.name for build in imported_builds})
        simc = Path(self._simc_path.text())
        if not simc.is_file():
            self._set_status(self._t("status.no_simc", "No se encontró simc.exe."))
            return
        self._running = True
        self._run.setEnabled(False)
        self._progress.setRange(0, 0)
        self._set_status(self._t("status.simulating", "Simulando con SimulationCraft."))
        outcome: Queue = Queue(maxsize=1)
        def execute() -> None:
            try:
                outcome.put((self._runner(self._export, simc, Path(self._addon_path.text()), root=self._root, selected_config_ids=selected, imported_loadouts=imported), None))
            except Exception as error:
                outcome.put((None, error))
        Thread(target=execute, daemon=True).start()
        self._wait_for_run(outcome)

    def _wait_for_run(self, outcome: Queue) -> None:
        try:
            result, error = outcome.get_nowait()
        except Empty:
            QtCore.QTimer.singleShot(50, lambda: self._wait_for_run(outcome))
            return
        self._running = False
        self._run.setEnabled(True)
        self._progress.setRange(0, 1)
        self._progress.setValue(1)
        if error is not None:
            self._set_status(f"No se generó comparación: {error}")
            return
        if self._import_targets:
            generated = tuple(identifier for identifier, _ in result.loadouts if identifier < 0); mapping = dict(zip(generated, self._import_targets))
            result = replace(result, loadouts=tuple((mapping.get(identifier, identifier), value) for identifier, value in result.loadouts), preferred_loadout=mapping.get(result.preferred_loadout, result.preferred_loadout), score_weights=tuple(replace(weight, build_id=mapping.get(weight.build_id, weight.build_id)) for weight in result.score_weights), relative_errors=tuple((mapping.get(identifier, identifier), value) for identifier, value in result.relative_errors), run_ids=tuple((mapping.get(identifier, identifier), value) for identifier, value in result.run_ids))
        if self._saved_id_map:
            self._names.update({original: self._names.get(generated, f"Build {original}") for generated, original in self._saved_id_map.items()})
            result = replace(result, loadouts=tuple((self._saved_id_map.get(identifier, identifier), value) for identifier, value in result.loadouts), preferred_loadout=self._saved_id_map.get(result.preferred_loadout, result.preferred_loadout), score_weights=tuple(replace(weight, build_id=self._saved_id_map.get(weight.build_id, weight.build_id)) for weight in result.score_weights), relative_errors=tuple((self._saved_id_map.get(identifier, identifier), value) for identifier, value in result.relative_errors), run_ids=tuple((self._saved_id_map.get(identifier, identifier), value) for identifier, value in result.run_ids))
        self._comparison = result; self.show_comparison(result); self._save_character_scores(result)
        try:
            if self._remember.isChecked(): _save_paths(_settings_path(), "bundled" if _bundled_simc() else self._simc_path.text(), self._addon_path.text())
            else: _clear_paths(_settings_path())
        except OSError: pass
        self._set_status(f"{self._skipped}{result.message} {self._t('status.results_saved', 'Los resultados se guardaron localmente.')}")

    def show_comparison(self, result: LoadoutComparison) -> None:
        equipment = () if self._snapshot is None else self._snapshot.equipped
        self._table.show_table(comparison_table(result, self._names, equipment), self._t("table.stat", "Estadística"))
        self._details.setPlainText(result.message + "\n" + self._t("details.comparison", "La tabla muestra DPS."))

    def _save_character_scores(self, result: LoadoutComparison) -> None:
        try:
            snapshot = parse_live_analysis_export(self._export)
            if not self._saved_profile_mode: self._prepare_profile(snapshot)
            elif self._character is None: raise ItemScoreProfileError("character_profile_unavailable")
            for weight in result.score_weights: self._character = store_weight(self._character, weight)
            self._character = store_simulation_results(self._character, result.specialization_id, result.loadouts, result.score_weights, result.relative_errors, result.run_ids)
            self._persist_profile()
        except (ItemScoreProfileError, OSError, ValueError): self._set_status("La comparación se mostró, pero no se pudo guardar el perfil local.")

    def _export_chosen_scores(self) -> None:
        if self._comparison is None or self._character is None:
            self._set_status("Ejecuta una simulación y guarda el perfil antes de exportar pesos."); return
        selected = self._selected_ids(); available = {weight.build_id for weight in self._comparison.score_weights if weight.build_id is not None and weight.build_id > 0}
        chosen = tuple((self._comparison.specialization_id, build_id) for build_id in selected if build_id in available)
        if not chosen:
            self._set_status("Selecciona una build real que haya sido simulada; las cadenas externas no se pueden atribuir a un loadout de WoW."); return
        try: write_item_score_profiles(Path(self._addon_path.text()), self._character, chosen)
        except (OSError, ValueError):
            self._set_status("No se pudieron exportar los pesos al addon seleccionado."); return
        names = ", ".join(self._names.get(build_id, f"Loadout {build_id}") for _, build_id in chosen)
        self._set_status(f"Pesos exportados para {names}. En WoW usa /reload y revisa el tooltip del ítem.")

    def _one_selected_real_build(self) -> int | None:
        selected = self._selected_ids(); return selected[0] if len(selected) == 1 and selected[0] > 0 else None

    def _copy_weights(self) -> None:
        build_id = self._one_selected_real_build()
        if self._comparison is None or build_id is None:
            self._set_status("Selecciona una sola build real ya simulada para copiar sus pesos."); return
        weight = next((value for value in self._comparison.score_weights if value.build_id == build_id), None)
        if weight is None:
            self._set_status("La build seleccionada no tiene pesos simulados disponibles."); return
        self._application.clipboard().setText(encode_weight_transfer(weight, self._names.get(build_id, f"Loadout {build_id}")))
        self._set_status("Pesos copiados. En WoW abre /dpslab scores y usa ‘Importar pegado’.")

    def _paste_weights(self) -> None:
        build_id = self._one_selected_real_build()
        if not self._export or build_id is None:
            self._set_status("Selecciona una sola build real para recibir los pesos pegados."); return
        try:
            snapshot = parse_live_analysis_export(self._export)
            name, weight = decode_weight_transfer(self._application.clipboard().text(), class_id=snapshot.class_id, build_id=build_id)
            if weight.specialization_id != snapshot.specialization_id: raise LoadoutRecommendationError("weight_transfer_invalid")
            self._prepare_profile(snapshot); self._character = store_weight(self._character, weight); self._persist_profile()
        except Exception:
            self._set_status("El portapapeles no contiene pesos válidos para esta especialización."); return
        self._set_status(f"Pesos manuales '{name}' guardados en {self._names.get(build_id, build_id)}.")

    def _save_case(self) -> None:
        if self._comparison is None:
            self._set_status("Ejecuta una comparación antes de guardar el caso."); return
        try: save_case(self._root, self._case_title.text(), self._export, self._comparison)
        except LoadoutComparisonLibraryError:
            self._set_status("No se pudo guardar el caso."); return
        self._set_status(f"Caso '{self._case_title.text().strip()}' guardado localmente: comparación y resultados. No modifica el perfil.")

    def _clear_workspace(self) -> None:
        if self._running:
            self._set_status("Espera a que termine la simulación antes de limpiar la interfaz."); return
        if QtWidgets.QMessageBox.question(self, self._t("dialog.clear_title", "Limpiar interfaz"), self._t("dialog.clear_text", "¿Continuar?")) != QtWidgets.QMessageBox.StandardButton.Yes:
            return
        self._export = ""; self._snapshot = None; self._ids = (); self._build_ids = (); self._names = {}; self._unavailable = {}; self._saved_id_map = {}; self._saved_profile_mode = False; self._comparison = None; self._character = None
        self._imports.clear(); self._case_title.setText("Comparación de loadouts"); self._character_name.clear(); self._realm.clear(); self._profile_name.clear(); self._title.setText("DpsLab — Comparación de loadouts")
        self._profiles.setCurrentIndex(-1); self._builds.clear(); self._details.clear(); self._table.clearContents(); self._table.setRowCount(0); self._table.setColumnCount(0)
        self._set_status(self._t("status.cleared", "Interfaz limpia."))

    def run(self) -> None:
        self.show()
        if self._owned_application:
            self._application.exec()
