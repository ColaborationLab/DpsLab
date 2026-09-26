"""Read-only equipment and loadout presentation; never attributes DPS to items."""
from __future__ import annotations

import math
import re
from PySide6 import QtCore, QtWidgets


def percentage_label(value, reference, parent=None):
    label = QtWidgets.QLabel(parent)
    if reference > 0 and math.isfinite(value) and math.isfinite(reference):
        delta = (value / reference - 1) * 100
        if abs(delta) >= 0.005:
            label.setText(f"{'↑' if delta > 0 else '↓'} ({delta:+.2f} %)")
            label.setProperty("role", "positive" if delta > 0 else "negative")
    return label


def item_name(item):
    match = re.search(r"\[([^\]]+)\]", item.item_link)
    return match.group(1) if match else f"Item #{item.item_id}"


class GearCards(QtWidgets.QScrollArea):
    def __init__(self, translate, parent=None):
        super().__init__(parent)
        self.t = translate
        self.setWidgetResizable(True)
        self.reset()

    def reset(self):
        previous = self.takeWidget()
        if previous:
            previous.hide()
            previous.deleteLater()
        body = QtWidgets.QWidget()
        body.setObjectName('transparentContent')
        self.viewport().setAutoFillBackground(False)
        body.setAutoFillBackground(False)
        self.content = QtWidgets.QVBoxLayout(body)
        self.content.setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetMinimumSize)
        self.setWidget(body)

    def label(self, text):
        label = QtWidgets.QLabel(text)
        label.setTextFormat(QtCore.Qt.TextFormat.PlainText)
        label.setWordWrap(True)
        return label

    def show_equipment(self, equipment, comparison=None, names=None, reference_id=None):
        self.reset()
        names = names or {}
        if comparison and comparison.loadouts:
            scores = dict(comparison.loadouts)
            reference = scores.get(reference_id, max(scores.values()))
            builds = QtWidgets.QHBoxLayout()
            for identifier, score in comparison.loadouts[:4]:
                frame = QtWidgets.QFrame()
                frame.setObjectName("card")
                column = QtWidgets.QVBoxLayout(frame)
                column.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
                column.addWidget(self.label(names.get(identifier, str(identifier))))
                column.addWidget(self.label(f"{score:,.0f} {comparison.metric}"))
                column.addWidget(percentage_label(score, reference))
                weights = next((w.values for w in comparison.score_weights if w.build_id == identifier), ())
                weight_text = " · ".join(f"{self.t('gear.stat.' + stat, stat)}: {value:.2f}" for stat, value in weights)
                if weight_text:
                    column.addWidget(self.label(weight_text))
                builds.addWidget(frame)
            self.content.addLayout(builds)
            self.content.addWidget(self.label(self.t("gear.shared", "Same exported equipment for every loadout. No item substitutions were simulated; item stat deltas are not available.")))
        grid = QtWidgets.QGridLayout()
        grid.setSpacing(6)
        for index, item in enumerate(equipment):
            frame = QtWidgets.QFrame()
            frame.setObjectName("card")
            column = QtWidgets.QVBoxLayout(frame)
            column.setContentsMargins(8, 5, 8, 5)
            column.setSpacing(2)
            column.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
            row = QtWidgets.QHBoxLayout()
            icon = self.label("◇")
            icon.setFixedSize(30, 30)
            icon.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            icon.setToolTip(self.t("gear.icon_missing", "Local item icon unavailable. This symbol is not the item icon."))
            row.addWidget(icon)
            title = self.label(item_name(item))
            title.setMaximumHeight(36)
            title.setToolTip(item_name(item))
            row.addWidget(title, 1)
            column.addLayout(row)
            column.addWidget(self.label(f"{self.t('gear.slot.' + item.slot, item.slot)} · {self.t('gear.level', 'Item level')} {item.item_level}"))
            stats = "\n".join(f"{self.t('gear.stat.' + stat, stat)}: {amount:g}" for stat, amount in item.stats)
            frame.setToolTip(stats or self.t("gear.no_stats", "No item stats in this export."))
            frame.setAccessibleName(f'{item_name(item)}; {item.item_level}; {stats}')
            frame.setMaximumHeight(86)
            frame.setMinimumHeight(68)
            grid.addWidget(frame, index // 2, index % 2)
        self.content.addLayout(grid)
        if not equipment:
            self.content.addWidget(self.label(self.t("gear.empty", "Import or open a character profile to view equipped items.")))
        self.content.addStretch(1)
        self.content.activate()
        self.widget().setMinimumHeight(self.content.minimumSize().height())

    def show_recommendations(self, comparison, names):
        self.reset()
        if comparison and comparison.loadouts:
            best_id, best = max(comparison.loadouts, key=lambda pair: pair[1])
            number = 0
            for identifier, score in comparison.loadouts:
                if score <= 0 or score >= best:
                    continue
                number += 1
                self.content.addWidget(self.label(f"{number}. {names.get(identifier, str(identifier))} → {names.get(best_id, str(best_id))}"))
                self.content.addWidget(percentage_label(best, score))
            if not number:
                self.content.addWidget(self.label(self.t("gear.no_action", "No higher-DPS alternative in this comparison.")))
            self.content.addWidget(self.label(self.t("gear.action_limit", "Alternative loadout changes, not cumulative gains. Simulated DPS for this scenario; not individual item contributions.")))
        else:
            self.content.addWidget(self.label(self.t("gear.no_results", "Run a comparison to obtain suggested actions.")))
        self.content.addStretch(1)
