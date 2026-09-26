"""Foundry overview built from the same live comparison used by Simulation."""
from PySide6 import QtCore, QtWidgets

from .dpsfoundry_theme import StatePanel, foundry_icon
from .foundry_chrome import FoundryBackdrop, soft_glow
from .foundry_gear import percentage_label


class FoundryDashboard(QtWidgets.QScrollArea):
    def __init__(self, navigate, translate, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.t = translate
        body = FoundryBackdrop()
        body.setObjectName("foundryBackdrop")
        self.setWidget(body)
        layout = QtWidgets.QVBoxLayout(body)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(18)
        heading = QtWidgets.QHBoxLayout()
        titles = QtWidgets.QVBoxLayout()
        titles.addWidget(self.label(self.t("foundry.overview", "Overview"), "eyebrow"))
        titles.addWidget(self.label(self.t("foundry.home", "Your next improvement starts here"), "pageTitle"))
        self.context = self.label(self.t("foundry.no_profile", "No active profile"), "muted")
        titles.addWidget(self.context)
        heading.addLayout(titles, 1)
        self.action = QtWidgets.QPushButton(self.t("foundry.import", "Import from Link"))
        self.action.setProperty("primary", True)
        self.action.setIcon(foundry_icon("link", "#17120d"))
        self.action.clicked.connect(lambda: navigate("simulation"))
        heading.addWidget(self.action)
        layout.addLayout(heading)

        metrics = QtWidgets.QHBoxLayout()
        self.values = []
        for key, title, icon in (("dps", "SIMULATED DPS", "simulation"), ("builds", "LOADOUTS", "compare"), ("weights", "STAT WEIGHTS", "settings")):
            card, content = self.card()
            row = QtWidgets.QHBoxLayout()
            symbol = QtWidgets.QLabel()
            symbol.setPixmap(foundry_icon(icon, "#f28c28").pixmap(28, 28))
            soft_glow(symbol, '#ff991f', 14)
            row.addWidget(symbol)
            column = QtWidgets.QVBoxLayout()
            value = self.label("—", "metric")
            soft_glow(value, '#dae6eb', 7)
            self.values.append(value)
            column.addWidget(value)
            column.addWidget(self.label(self.t("foundry.metric." + key, title), "section"))
            row.addLayout(column, 1)
            content.addLayout(row)
            metrics.addWidget(card, 1)
        layout.addLayout(metrics)

        grid = QtWidgets.QGridLayout()
        grid.setSpacing(16)
        results, result_layout = self.card(self.t("foundry.results", "LOADOUT PERFORMANCE"))
        self.reference = QtWidgets.QComboBox()
        self.reference.setAccessibleName(self.t("foundry.reference", "DPS reference"))
        self.reference.setToolTip(self.t("foundry.reference_help", "Compare with the highest DPS in this simulation, or choose a simulated build. Negative percentages mean DPS lost relative to that reference."))
        self.reference.currentIndexChanged.connect(self.render_results)
        result_layout.addWidget(self.reference)
        self.result_rows = QtWidgets.QVBoxLayout()
        self.result_rows.setSpacing(12)
        result_layout.addLayout(self.result_rows)
        result_layout.addStretch(1)
        view = QtWidgets.QPushButton(self.t("foundry.view_results", "View comparison →"))
        view.clicked.connect(lambda: navigate("compare"))
        result_layout.addWidget(view, 0, QtCore.Qt.AlignmentFlag.AlignRight)
        grid.addWidget(results, 0, 0)
        weights, weights_layout = self.card(self.t("foundry.weights", "STAT WEIGHTS"))
        self.weight_rows = QtWidgets.QVBoxLayout()
        self.weight_rows.setSpacing(10)
        weights_layout.addLayout(self.weight_rows)
        weights_layout.addStretch(1)
        grid.addWidget(weights, 0, 1)
        next_card, next_layout = self.card(self.t("foundry.next", "NEXT STEP"))
        self.state = StatePanel()
        next_layout.addWidget(self.state)
        actions = QtWidgets.QHBoxLayout()
        for key, text, target in (("profile", "Open profile", "character"), ("run", "Prepare simulation", "simulation")):
            button = QtWidgets.QPushButton(self.t("foundry." + key, text))
            button.setIcon(foundry_icon(target))
            button.clicked.connect(lambda checked=False, route=target: navigate(route))
            actions.addWidget(button)
        next_layout.addLayout(actions)
        grid.addWidget(next_card, 1, 0)
        sync, sync_layout = self.card("DPSFOUNDRY LINK")
        self.sync_text = self.label("", "muted")
        self.sync_text.setWordWrap(True)
        sync_layout.addWidget(self.sync_text)
        sync_layout.addStretch(1)
        button = QtWidgets.QPushButton(self.t("foundry.sync", "Open sync center →"))
        button.clicked.connect(lambda: navigate("link"))
        sync_layout.addWidget(button)
        grid.addWidget(sync, 1, 1)
        grid.setColumnStretch(0, 3)
        grid.setColumnStretch(1, 2)
        grid.setRowMinimumHeight(0, 230)
        layout.addLayout(grid, 1)
        layout.addWidget(self.label(self.t("foundry.footer", "ANALYZE  /  DECIDE  /  SYNC  /  PLAY  /  REFINE"), "eyebrow"))
        self.update_data(None, {}, 0, None, False)

    @staticmethod
    def label(text, role):
        label = QtWidgets.QLabel(text)
        label.setProperty("role", role)
        label.setWordWrap(True)
        return label

    def card(self, title=""):
        frame = QtWidgets.QFrame()
        frame.setObjectName("card")
        layout = QtWidgets.QVBoxLayout(frame)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(16)
        if title:
            layout.addWidget(self.label(title, "section"))
        return frame, layout

    def fill_rows(self, layout, rows, empty, reference=None):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().hide()
                item.widget().deleteLater()
        if not rows:
            label = self.label(empty, "muted")
            label.setMinimumHeight(95)
            layout.addWidget(label)
            return
        maximum = max(value for _, value in rows)
        for name, value in rows:
            widget = QtWidgets.QWidget()
            column = QtWidgets.QVBoxLayout(widget)
            column.setContentsMargins(0, 0, 0, 0)
            row = QtWidgets.QHBoxLayout()
            row.addWidget(self.label(name, "muted"), 1)
            text = f"{value:,.1f}"
            row.addWidget(self.label(text, "accent"))
            if reference is not None:
                row.addWidget(percentage_label(value, reference))
            column.addLayout(row)
            bar = QtWidgets.QProgressBar()
            bar.setRange(0, 1000)
            bar.setValue(round(1000 * max(value, 0) / maximum) if maximum > 0 else 0)
            bar.setTextVisible(False)
            bar.setFixedHeight(6)
            column.addWidget(bar)
            layout.addWidget(widget)

    def update_data(self, comparison, names, build_count, character, has_export):
        profile = (character.profile_name or character.name) if character else self.t("foundry.no_profile", "No active profile")
        self.context.setText(profile)
        results = sorted(comparison.loadouts, key=lambda item: item[1], reverse=True) if comparison else []
        weights = next((item.values for item in comparison.score_weights if item.build_id == comparison.preferred_loadout), ()) if comparison else ()
        self.values[0].setText(f"{results[0][1]:,.0f}" if results else "—")
        self.values[1].setText(str(build_count))
        self.values[2].setText(str(len(weights)) if weights else "—")
        self._results = results
        self._names = dict(names)
        selected = self.reference.currentData()
        self.reference.blockSignals(True)
        self.reference.clear()
        self.reference.addItem(self.t("foundry.best_reference", "Reference: highest simulated DPS"), None)
        for key, value in results:
            self.reference.addItem(names.get(key, str(key)), key)
        self.reference.setCurrentIndex(max(0, self.reference.findData(selected)))
        self.reference.setEnabled(len(results) > 1)
        self.reference.blockSignals(False)
        self.render_results()
        self.fill_rows(self.weight_rows, [(key, value) for key, value in weights], self.t("foundry.empty_weights", "Personalized weights will appear after a simulation. No estimated values are shown here."))
        self.sync_text.setText(self.t("foundry.link_ready", "Character export received. Transfer weights to Link after reviewing the simulation.") if has_export else self.t("foundry.link_empty", "Export your character from Link in WoW, then import it here. Your saved profiles also work while the game is closed."))
        state = "success" if comparison else "ready" if has_export else "empty"
        self.state.set_state(state)
        self.state._title.setText(self.t("foundry.state." + state, state))
        self.state._detail.setText(self.t("foundry.step." + state, ""))

    def render_results(self, *_):
        results = getattr(self, '_results', [])
        names = getattr(self, '_names', {})
        reference_id = self.reference.currentData()
        reference = dict(results).get(reference_id, results[0][1] if results else 0)
        self.fill_rows(self.result_rows, [(names.get(key, str(key)), value) for key, value in results], self.t("foundry.empty_results", "No simulation yet. Import a character or open a saved profile to compare its loadouts."), reference if len(results) > 1 else None)
