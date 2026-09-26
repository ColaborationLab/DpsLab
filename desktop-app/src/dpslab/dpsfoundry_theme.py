"""Small, semantic Qt theme layer shared by DpsFoundry presentation widgets."""
from __future__ import annotations

from dataclasses import dataclass

from PySide6 import QtCore, QtGui, QtWidgets


@dataclass(frozen=True)
class FoundryTheme:
    theme_id: str
    label: str
    root: str
    panel: str
    raised: str
    input: str
    primary: str
    secondary: str
    muted: str
    accent: str
    accent_secondary: str
    success: str
    warning: str
    error: str
    info: str
    border: str
    focus: str


THEMES = {
    "foundry": FoundryTheme("foundry", "Foundry", "#080e12", "#121b21", "#2a3138", "#080e12", "#edf1f4", "#c7cdd6", "#929da6", "#ff8a00", "#c66019", "#70c36b", "#ffc86b", "#ef7868", "#6fb6d9", "#465056", "#ffc86b"),
    "arcane_vanguard": FoundryTheme("arcane_vanguard", "Arcane Vanguard", "#10121b", "#1b1d2b", "#252a3a", "#10131d", "#f2f4ff", "#c0c5da", "#8d94ae", "#9d69ee", "#50d0e2", "#70cfa8", "#e1af58", "#ef747d", "#5dbde7", "#414661", "#b88cff"),
    "runebound_command": FoundryTheme("runebound_command", "Runebound Command", "#101822", "#172534", "#203447", "#101b27", "#f1f7fb", "#c1d1dc", "#8ba0ad", "#56c5dc", "#d5aa55", "#76ce9a", "#deb35b", "#ea7474", "#68c6e0", "#36506a", "#78d9ee"),
    "celestial_foundry": FoundryTheme("celestial_foundry", "Celestial Foundry", "#101827", "#18233a", "#223250", "#111b2d", "#f7f4e9", "#d4d2c6", "#9b9fa8", "#d5ad52", "#a9d3ed", "#82cc91", "#dfb963", "#e57679", "#83c8e9", "#40516d", "#e7c879"),
}

STATE_DETAILS = {
    "loading": ("Loading", "Working on this step. You can keep using the rest of Core."),
    "ready": ("Ready", "This information is ready to review."),
    "empty": ("Nothing here yet", "Complete the previous step to add data here."),
    "unavailable": ("Unavailable", "This capability is not available with the current local data."),
    "error": ("Needs attention", "The action could not be completed. Review the next step below."),
    "blocked": ("Blocked", "A required condition must be resolved before continuing."),
    "success": ("Completed", "The latest action completed successfully."),
}


def theme_style(theme: FoundryTheme) -> str:
    shade = QtGui.QColor(theme.panel)
    surface = f"rgba({shade.red()}, {shade.green()}, {shade.blue()}, 178)"
    header = '#030708' if theme.theme_id == 'foundry' else theme.raised
    warm = '#51341d' if theme.theme_id == 'foundry' else theme.raised
    def blend(base, accent, amount):
        a, b = QtGui.QColor(base), QtGui.QColor(accent)
        return QtGui.QColor(*(round(x+(y-x)*amount) for x, y in zip(a.getRgb()[:3], b.getRgb()[:3]))).name()
    hover = blend(theme.raised, warm, .45)
    hover_border = blend(theme.border, theme.accent_secondary, .5)
    run_surface = blend(theme.raised, warm, .3)
    run_border = blend(theme.border, theme.accent, .3)
    run_hover = blend(theme.raised, theme.accent_secondary, .3)
    return f"""
    QWidget {{ color: {theme.primary}; font-family: 'Segoe UI'; font-size: 13px; }}
    QMainWindow, QWidget#dpsfoundryRoot, QFrame#foundryFrame {{ background: {theme.root}; }}
    QLabel {{ background: transparent; border: none; }}
    QFrame#topBar {{ background: qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 {header},stop:1 {theme.root}); border-bottom: 1px solid {theme.border}; border-top: 2px solid {theme.accent}; }}
    QFrame#sidebar {{ background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 {theme.panel},stop:1 {theme.root}); border-right: 1px solid {theme.border}; }}
    QFrame#card {{ background: {surface}; border: 1px solid {theme.border}; border-radius: 4px; }}
    QFrame#statePanel {{ background: transparent; border: none; border-left: 2px solid {theme.info}; }}
    QLabel[role="positive"] {{ color: {theme.success}; font-weight: 600; }}
    QLabel[role="negative"] {{ color: {theme.error}; font-weight: 600; }}
    QListWidget::item {{ padding: 10px; border: 1px solid transparent; border-bottom-color: {theme.border}; border-left: 3px solid transparent; }}
    QListWidget::item:hover {{ background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 {hover},stop:1 {theme.panel}); border-color: {hover_border}; }}
    QListWidget::item:selected {{ border-color: {theme.accent}; border-left: 3px solid {theme.focus}; background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 {warm},stop:.5 {theme.raised},stop:1 {theme.panel}); color: {theme.primary}; }}
    QLabel[role="brand"] {{ font-size: 25px; font-weight: 800; letter-spacing: 1px; }}
    QLabel[role="brandModule"] {{ font-size: 25px; font-weight: 700; letter-spacing: 2px; color: {theme.accent}; }}
    QLabel[role="brandDescriptor"] {{ font-size: 10px; letter-spacing: 2px; color: {theme.secondary}; }}
    QLabel[role="pageTitle"] {{ font-size: 25px; font-weight: 600; }}
    QLabel[role="metric"] {{ font-size: 27px; font-weight: 600; }}
    QLabel[role="section"] {{ font-size: 11px; font-weight: 700; letter-spacing: 1px; color: {theme.secondary}; }}
    QLabel[role="accent"] {{ color: {theme.accent}; }}
    QScrollArea, QStackedWidget {{ border: none; background: transparent; }}
    QScrollArea > QWidget > QWidget {{ background: transparent; }}
    QWidget#transparentContent {{ background: transparent; }}
    QWidget#foundryBackdrop {{ background: transparent; }}
    QGroupBox {{ background: {surface}; border: 1px solid {theme.border}; border-radius: 6px; margin-top: 10px; padding: 11px 8px 8px 8px; font-weight: 600; }}
    QGroupBox::title {{ subcontrol-origin: margin; left: 10px; padding: 0 4px; color: {theme.secondary}; }}
    QLabel[role="muted"] {{ color: {theme.secondary}; }} QLabel[role="eyebrow"] {{ color: {theme.accent}; font-size: 10px; font-weight: 700; letter-spacing: 2px; }}
    QLabel[role="stateTitle"] {{ font-weight: 700; }} QLabel[role="stateDetail"] {{ color: {theme.secondary}; }}
    QLabel[role="badge"] {{ background: {theme.input}; color: {theme.secondary}; border: 1px solid {theme.border}; border-radius: 11px; padding: 4px 12px; font-size: 11px; font-weight: 600; }}
    QLabel[role="badge"][state="ready"], QLabel[role="badge"][state="success"] {{ color: {theme.success}; border-color: {theme.success}; }}
    QLabel[role="badge"][state="loading"] {{ color: {theme.accent}; border-color: {theme.accent_secondary}; }}
    QLabel[role="badge"][state="error"] {{ color: {theme.error}; border-color: {theme.error}; }}
    QLabel[role="badge"][state="blocked"] {{ color: {theme.warning}; border-color: {theme.warning}; }}
    QLineEdit, QPlainTextEdit, QListWidget, QTableWidget, QComboBox {{ background: {theme.input}; color: {theme.primary}; border: 1px solid {theme.border}; border-radius: 4px; padding: 5px; }}
    QTableWidget {{ gridline-color: {theme.border}; }} QHeaderView::section {{ background: {theme.raised}; color: {theme.primary}; border: 0; padding: 7px; font-weight: 700; }}
    QPushButton {{ background: qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 {theme.raised},stop:1 {theme.panel}); color: {theme.primary}; border: 1px solid {theme.border}; border-radius: 3px; padding: 9px 12px; }}
    QPushButton:hover {{ border-color: {hover_border}; background: qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 {hover},stop:.5 {theme.raised},stop:1 {theme.panel}); }}
    QPushButton:pressed {{ border-color: {theme.focus}; background: {theme.accent_secondary}; color: {theme.primary}; }}
    QPushButton:focus, QLineEdit:focus, QComboBox:focus {{ border: 1px solid {theme.focus}; }}
    QPushButton:disabled {{ color: {theme.muted}; background: {theme.input}; border-color: {theme.border}; }}
    QPushButton[windowControl="true"] {{ padding: 0; background: transparent; border: none; font-size: 18px; color: {theme.secondary}; }}
    QPushButton[windowControl="true"]:hover {{ background: {theme.raised}; color: {theme.accent}; }}
    QPushButton[primary="true"] {{ background: qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 {warm},stop:1 {theme.input}); color: {theme.primary}; border-color: {theme.accent}; font-weight: 700; }}
    QPushButton[primary="true"]:hover {{ background: qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 {theme.accent_secondary},stop:1 {warm}); border-color: {theme.focus}; }}
    QPushButton[primary="true"]:pressed {{ background: {theme.accent}; color: #17120d; }}
    QPushButton[primary="true"]:disabled {{ background: {theme.input}; color: {theme.muted}; border-color: {theme.border}; }}
    QPushButton[primary="true"][subdued="true"] {{ background: qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 {run_surface},stop:1 {theme.panel}); border-color: {run_border}; font-weight: 600; }}
    QPushButton[primary="true"][subdued="true"]:hover {{ background: {run_hover}; border-color: {run_border}; }}
    QPushButton[primary="true"][subdued="true"]:pressed {{ background: {run_surface}; border-color: {theme.focus}; color: {theme.primary}; }}
    QPushButton[primary="true"][subdued="true"]:disabled {{ background: {theme.input}; border-color: {theme.border}; color: {theme.muted}; }}
    QPushButton[nav="true"] {{ text-align: left; border: 1px solid transparent; border-left: 3px solid transparent; padding: 12px; background: rgba({shade.red()}, {shade.green()}, {shade.blue()}, 175); color: {theme.secondary}; }}
    QPushButton[nav="true"]:hover {{ background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 {hover},stop:1 {theme.panel}); border-color: {hover_border}; color: {theme.primary}; }}
    QPushButton[nav="true"][active="true"] {{ background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 {warm},stop:.5 {theme.raised},stop:1 {theme.panel}); border: 1px solid {theme.accent}; border-left: 3px solid {theme.focus}; color: {theme.primary}; }}
    QPushButton[nav="true"]:pressed {{ background: {theme.accent_secondary}; border-color: {theme.focus}; }}
    QMenu, QComboBox QAbstractItemView {{ background: {theme.panel}; color: {theme.primary}; border: 1px solid {theme.border}; selection-background-color: {theme.raised}; selection-color: {theme.primary}; padding: 5px; }}
    QMenu::item:selected {{ background: {theme.raised}; }}
    QTableWidget::item:selected {{ background: {theme.raised}; color: {theme.primary}; }}
    QScrollBar:vertical {{ background: {theme.root}; width: 10px; }}
    QScrollBar::handle:vertical {{ background: {theme.border}; min-height: 25px; border-radius: 4px; }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
    QSpinBox {{ background: {theme.input}; color: {theme.primary}; border: 1px solid {theme.border}; padding: 6px; }}
    QProgressBar {{ background: {theme.input}; border: 1px solid {theme.border}; border-radius: 2px; text-align: center; }} QProgressBar::chunk {{ background: {theme.accent}; }}
    QToolTip {{ background: {theme.raised}; color: {theme.primary}; border: 1px solid {theme.focus}; padding: 5px; }}
    """


class StateBadge(QtWidgets.QLabel):
    """Non-interactive, translated text plus semantic colour; no fake status."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setProperty('role', 'badge')
        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Maximum, QtWidgets.QSizePolicy.Policy.Fixed)
        self.setTextFormat(QtCore.Qt.TextFormat.PlainText)

    def set_state(self, state, text, detail=''):
        if state not in STATE_DETAILS:
            raise ValueError('dpsfoundry_state_invalid')
        self.setProperty('state', state)
        self.setText(text)
        self.setToolTip(detail)
        self.setAccessibleName(text)
        self.style().unpolish(self)
        self.style().polish(self)


class StatePanel(QtWidgets.QFrame):
    """Textual state feedback; colour is only a secondary cue."""
    def __init__(self, state: str = "empty", detail: str = "", parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("statePanel")
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        self._title = StateBadge()
        self._detail = QtWidgets.QLabel()
        self._detail.setProperty("role", "stateDetail")
        self._detail.setWordWrap(True)
        layout.addWidget(self._title)
        layout.addWidget(self._detail)
        self.set_state(state, detail)

    @property
    def state(self) -> str:
        return self.property("state")

    def set_state(self, state: str, detail: str = "") -> None:
        if state not in STATE_DETAILS:
            raise ValueError("dpsfoundry_state_invalid")
        title, default_detail = STATE_DETAILS[state]
        self.setProperty("state", state)
        self._title.set_state(state, title, detail or default_detail)
        self._detail.setText(detail or default_detail)
        self.style().unpolish(self)
        self.style().polish(self)


def apply_theme(widget: QtWidgets.QWidget, theme_id: str) -> FoundryTheme:
    theme = THEMES.get(theme_id, THEMES["foundry"])
    widget.setStyleSheet(theme_style(theme))
    return theme


def foundry_icon(name: str, color: str = "#c0c8c5", *, finish: str = 'plain') -> QtGui.QIcon:
    """Original line icons drawn at 4x; no external artwork or font glyphs."""
    if name == "forge":
        return forge_emblem(color)
    paths = {
        "home": [[(3,3),(10,3),(10,10),(3,10),(3,3)],[(14,3),(21,3),(21,10),(14,10),(14,3)],[(3,14),(10,14),(10,21),(3,21),(3,14)],[(14,14),(21,14),(21,21),(14,21),(14,14)]],
        "character": [[(9,3),(15,3),(17,7),(15,11),(9,11),(7,7),(9,3)],[(8,14),(16,14),(20,18),(20,21),(4,21),(4,18),(8,14)]],
        "simulation": [[(6,3),(20,12),(6,21),(6,3)]],
        "compare": [[(5,4),(5,20)],[(12,4),(12,20)],[(19,4),(19,20)],[(2,8),(8,8)],[(9,16),(15,16)],[(16,11),(22,11)]],
        "recommendations": [[(14,2),(5,14),(11,14),(10,22),(20,9),(14,9),(14,2)]],
        "link": [[(9,7),(12,4),(18,4),(21,7),(21,11),(16,16),(12,16)],[(15,17),(12,20),(6,20),(3,17),(3,13),(8,8),(12,8)],[(8,16),(16,8)]],
        "settings": [[(4,5),(20,5)],[(4,12),(20,12)],[(4,19),(20,19)],[(8,2),(8,8)],[(16,9),(16,15)],[(10,16),(10,22)]],
        "setup": [[(4,3),(20,3),(20,17),(4,17),(4,3)],[(8,21),(16,21)],[(12,17),(12,21)]],
        "forge": [[(2,9),(22,9),(18,13),(15,14),(15,18),(18,21),(6,21),(9,18),(9,14),(6,13),(2,9)],[(12,1),(12,5)],[(6,3),(8,5)],[(18,3),(16,5)]],
    }
    pixmap = QtGui.QPixmap(96, 96)
    pixmap.fill(QtCore.Qt.GlobalColor.transparent)
    painter = QtGui.QPainter(pixmap)
    painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
    painter.scale(4, 4)
    pen = QtGui.QPen(QtGui.QColor(color), 1.5)
    pen.setCapStyle(QtCore.Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(QtCore.Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen)
    for points in paths.get(name, paths["home"]):
        path = QtGui.QPainterPath(QtCore.QPointF(*points[0]))
        for point in points[1:]:
            path.lineTo(*point)
        if finish != 'plain':
            if finish in ('hover', 'active'):
                for width, alpha in ((5, 18), (3.6, 38), (2.5, 65)):
                    halo = QtGui.QColor(color)
                    halo.setAlpha(alpha if finish == 'active' else alpha // 2)
                    painter.setPen(QtGui.QPen(halo, width, QtCore.Qt.PenStyle.SolidLine, QtCore.Qt.PenCapStyle.RoundCap, QtCore.Qt.PenJoinStyle.RoundJoin))
                    painter.drawPath(path)
            painter.save()
            painter.translate(.3, .65)
            painter.setPen(QtGui.QPen(QtGui.QColor('#030608'), 2.1))
            painter.drawPath(path)
            painter.restore()
            bevel = QtGui.QLinearGradient(0, 2, 0, 22)
            bevel.setColorAt(0, QtGui.QColor('#fff0bb' if finish != 'metal' else '#f2f6f9'))
            bevel.setColorAt(.45, QtGui.QColor(color))
            bevel.setColorAt(1, QtGui.QColor(color).darker(145))
            painter.setPen(QtGui.QPen(QtGui.QBrush(bevel), 1.5, QtCore.Qt.PenStyle.SolidLine, QtCore.Qt.PenCapStyle.RoundCap, QtCore.Qt.PenJoinStyle.RoundJoin))
        if name == "forge" and len(points) > 4:
            fill = QtGui.QColor(color)
            fill.setAlpha(45)
            painter.fillPath(path, fill)
        painter.drawPath(path)
    painter.end()
    pixmap.setDevicePixelRatio(4)
    return QtGui.QIcon(pixmap)


class FoundryNavButton(QtWidgets.QPushButton):
    """Existing navigation behavior, with pre-rendered icon states only."""
    def set_icon_theme(self, name, theme, active):
        self._icon_active = active
        self._icon_states = {
            state: foundry_icon(name, theme.secondary if state == 'metal' else theme.accent,
                                finish=state if theme.theme_id == 'foundry' else 'plain')
            for state in ('metal', 'hover', 'active')
        }
        self._refresh_icon()

    def _refresh_icon(self):
        if hasattr(self, '_icon_states'):
            state = 'active' if self._icon_active else 'hover' if self.underMouse() or self.hasFocus() else 'metal'
            self.setIcon(self._icon_states[state])

    def enterEvent(self, event):
        super().enterEvent(event)
        self._refresh_icon()

    def leaveEvent(self, event):
        super().leaveEvent(event)
        self._refresh_icon()

    def focusInEvent(self, event):
        super().focusInEvent(event)
        self._refresh_icon()

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self._refresh_icon()

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.isEnabled() and getattr(self.window(), '_theme_id', 'foundry') == 'foundry':
            active = bool(self.property('active'))
            if active or self.underMouse() or self.hasFocus():
                painter = QtGui.QPainter(self)
                selection_light(painter, self.rect(), active)


def selection_light(painter, rect, active):
    """Shared static inset glow, never blurring text or repainting on a timer."""
    painter.save()
    painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
    painter.setBrush(QtCore.Qt.BrushStyle.NoBrush)
    for inset, alpha in ((1, 170), (2, 65), (3, 28), (4, 12)):
        painter.setPen(QtGui.QPen(QtGui.QColor(255, 157, 48, alpha if active else alpha//3), 1))
        painter.drawRoundedRect(QtCore.QRectF(rect).adjusted(inset, inset, -inset, -inset), 3, 3)
    if active:
        glow = QtGui.QLinearGradient(rect.left(), 0, rect.left()+18, 0)
        glow.setColorAt(0, QtGui.QColor(255, 171, 65, 115))
        glow.setColorAt(1, QtGui.QColor(255, 138, 0, 0))
        painter.fillRect(QtCore.QRectF(rect.left()+3, rect.top()+4, 15, rect.height()-8), glow)
    painter.restore()


class FoundrySelectionDelegate(QtWidgets.QStyledItemDelegate):
    def paint(self, painter, option, index):
        super().paint(painter, option, index)
        if option.widget and getattr(option.widget.window(), '_theme_id', 'foundry') == 'foundry':
            selected = bool(option.state & QtWidgets.QStyle.StateFlag.State_Selected)
            hover = bool(option.state & QtWidgets.QStyle.StateFlag.State_MouseOver)
            if selected or hover:
                selection_light(painter, option.rect, selected)


def forge_emblem(color: str = "#ff9b32") -> QtGui.QIcon:
    """Concept silhouette: broad hot face, hollow waist, flared foot and sparks."""
    pixmap = QtGui.QPixmap(384, 384)
    pixmap.fill(QtCore.Qt.GlobalColor.transparent)
    painter = QtGui.QPainter(pixmap)
    painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
    painter.scale(3.84, 3.84)
    outline = QtGui.QPainterPath(QtCore.QPointF(7, 40))
    for x, y in ((93,40),(79,52),(65,57),(63,61),(63,76),(75,89),
                 (25,89),(37,76),(37,61),(33,57),(23,53),(7,40)):
        outline.lineTo(x, y)
    # Static layered strokes, not a repaint timer or an expensive live blur.
    for width, alpha in ((13,9),(9,18),(6,42)):
        glow = QtGui.QColor(color); glow.setAlpha(alpha)
        painter.setPen(QtGui.QPen(glow, width))
        painter.drawPath(outline)
    metal = QtGui.QLinearGradient(0,40,0,89)
    metal.setColorAt(0,QtGui.QColor('#794318'))
    metal.setColorAt(.16,QtGui.QColor('#211910'))
    metal.setColorAt(.75,QtGui.QColor('#100f0d'))
    metal.setColorAt(1,QtGui.QColor('#623211'))
    painter.fillPath(outline, metal)
    edge = QtGui.QLinearGradient(0,38,0,91)
    edge.setColorAt(0,QtGui.QColor('#fff2ba'))
    edge.setColorAt(.18,QtGui.QColor(color))
    edge.setColorAt(.7,QtGui.QColor('#f98525'))
    edge.setColorAt(1,QtGui.QColor('#ffd378'))
    painter.setPen(QtGui.QPen(QtGui.QBrush(edge), 2.2, QtCore.Qt.PenStyle.SolidLine, QtCore.Qt.PenCapStyle.SquareCap, QtCore.Qt.PenJoinStyle.MiterJoin))
    painter.drawPath(outline)
    painter.drawLine(QtCore.QPointF(13,42),QtCore.QPointF(88,42))
    painter.drawLine(QtCore.QPointF(30,86),QtCore.QPointF(70,86))
    for a,b in (((50,10),(50,27)),((32,21),(39,29)),((68,21),(61,29))):
        painter.setPen(QtGui.QPen(QtGui.QColor(color),3.8))
        painter.drawLine(QtCore.QPointF(*a),QtCore.QPointF(*b))
        painter.setPen(QtGui.QPen(QtGui.QColor('#fff0b1'),1.2))
        painter.drawLine(QtCore.QPointF(*a),QtCore.QPointF(*b))
    painter.end()
    pixmap.setDevicePixelRatio(4)
    return QtGui.QIcon(pixmap)


class FoundryWordmark(QtWidgets.QLabel):
    """Accessible label with a static, bevelled metallic text treatment."""
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        font = QtGui.QFont('Bahnschrift', 20, QtGui.QFont.Weight.Bold)
        font.setPixelSize(28)
        font.setLetterSpacing(QtGui.QFont.SpacingType.AbsoluteSpacing, 1.1)
        path = QtGui.QPainterPath()
        path.addText(0, 0, font, self.text())
        bounds = path.boundingRect()
        if bounds.isEmpty():
            return
        scale = min((self.width()-4)/bounds.width(), (self.height()-4)/bounds.height())
        painter.translate(2, (self.height()-bounds.height()*scale)/2)
        painter.scale(scale,scale)
        painter.translate(-bounds.left(),-bounds.top())
        module = self.property('role') == 'brandModule'
        gradient = QtGui.QLinearGradient(0,bounds.top(),0,bounds.bottom())
        for position, shade in ((0,'#fff1c0' if module else '#ffffff'),(.42,'#ffc16d' if module else '#e2e7eb'),(.5,'#ff8a22' if module else '#87929c'),(1,'#e46c18' if module else '#cbd2d7')):
            gradient.setColorAt(position,QtGui.QColor(shade))
        painter.translate(0,1)
        painter.setPen(QtGui.QPen(QtGui.QColor('#080b0e'),2))
        painter.drawPath(path)
        painter.translate(0,-1)
        painter.setPen(QtGui.QPen(QtGui.QColor('#ffd088' if module else '#dfe5e9'),.55))
        painter.setBrush(gradient)
        painter.drawPath(path)
