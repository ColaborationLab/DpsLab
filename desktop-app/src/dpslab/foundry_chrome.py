"""Foundry window surfaces; native system movement/resizing keeps desktop behavior."""
from pathlib import Path
import random

from PySide6 import QtCore, QtGui, QtWidgets


class FoundryFrame(QtWidgets.QFrame):
    RIM = 16
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("foundryFrame")
        self.setMouseTracking(True)

    def edges(self, point):
        edges = QtCore.Qt.Edge(0)
        if self.window().isMaximized():
            return edges
        if point.x() < self.RIM: edges |= QtCore.Qt.Edge.LeftEdge
        if point.x() > self.width() - self.RIM: edges |= QtCore.Qt.Edge.RightEdge
        if point.y() < self.RIM: edges |= QtCore.Qt.Edge.TopEdge
        if point.y() > self.height() - self.RIM: edges |= QtCore.Qt.Edge.BottomEdge
        return edges

    def leaveEvent(self, event):
        self.unsetCursor()
        super().leaveEvent(event)

    def childEvent(self, event):
        super().childEvent(event)
        # Content must not inherit the rim's transient resize cursor.
        if event.polished() and isinstance(event.child(), QtWidgets.QWidget):
            event.child().setCursor(QtCore.Qt.CursorShape.ArrowCursor)

    def mousePressEvent(self, event):
        edges = self.edges(event.position())
        handle = self.window().windowHandle()
        if event.button() == QtCore.Qt.MouseButton.LeftButton and edges and handle:
            handle.startSystemResize(edges)
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        edges = self.edges(event.position())
        left, right, top, bottom = (QtCore.Qt.Edge.LeftEdge, QtCore.Qt.Edge.RightEdge, QtCore.Qt.Edge.TopEdge, QtCore.Qt.Edge.BottomEdge)
        cursor = QtCore.Qt.CursorShape.ArrowCursor
        if edges in (left | top, right | bottom): cursor = QtCore.Qt.CursorShape.SizeFDiagCursor
        elif edges in (left | bottom, right | top): cursor = QtCore.Qt.CursorShape.SizeBDiagCursor
        elif edges & (left | right): cursor = QtCore.Qt.CursorShape.SizeHorCursor
        elif edges & (top | bottom): cursor = QtCore.Qt.CursorShape.SizeVerCursor
        self.setCursor(cursor)
        super().mouseMoveEvent(event)

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        rect = self.rect().adjusted(1, 1, -2, -2)
        from .dpsfoundry_theme import THEMES
        theme = THEMES[getattr(self.window(), '_theme_id', 'foundry')]
        if theme.theme_id != 'foundry':
            painter.setPen(QtGui.QPen(QtGui.QColor(theme.border), 3))
            painter.drawRoundedRect(rect.adjusted(3, 3, -3, -3), 10, 10)
            painter.setPen(QtGui.QPen(QtGui.QColor(theme.accent), 1))
            painter.drawRoundedRect(rect.adjusted(10, 10, -10, -10), 6, 6)
            return
        # Sixteen physical pixels of layered bevel, not a single outline.
        tones = ('#171a19','#a0a49b','#535a56','#242b2a','#424742',
                 '#65685e','#454940','#343b36','#464c44','#30352f',
                 '#252b29','#77766b','#191e1d','#080d0e','#333c38')
        for inset, tone in enumerate(tones):
            gradient = QtGui.QLinearGradient(0, 0, self.width(), self.height())
            color = QtGui.QColor(tone)
            gradient.setColorAt(0, color.lighter(125))
            gradient.setColorAt(.35, color.darker(110))
            gradient.setColorAt(.7, color)
            gradient.setColorAt(1, color.darker(150))
            painter.setPen(QtGui.QPen(QtGui.QBrush(gradient), 1))
            painter.drawRect(rect.adjusted(inset, inset, -inset, -inset))
        # Restrained wear on the metal rail, deterministic between repaints.
        painter.setPen(QtGui.QColor(190, 181, 152, 55))
        for x in range(30, self.width()-30, 23):
            y = 5 + (x * 7) % 6
            painter.drawLine(x, y, x+5, y+1)
            painter.drawLine(x, self.height()-y, x+3, self.height()-y-2)
        # Fixed seed: hammer marks and chips never flicker while repainting.
        rng = random.Random(42)
        # Uneven forged segments, with chipped inner edges and oxidized seams.
        for horizontal, length in ((True, self.width()), (False, self.height())):
            offset = 34
            while offset < length-34:
                end = min(offset+rng.randint(48, 112), length-34)
                inner = rng.randint(10, 14)
                contour = [(offset, 3), (end-4, 2), (end, 5), (end-2, inner),
                           (end-12, inner-2), (offset+12, inner+1), (offset, inner-1)]
                for opposite in (False, True):
                    points = []
                    for along, depth in contour:
                        across = (self.height() if horizontal else self.width())-depth if opposite else depth
                        points.append(QtCore.QPointF(along, across) if horizontal else QtCore.QPointF(across, along))
                    painter.setBrush(QtGui.QColor(rng.choice(('#393b32', '#443e31', '#303734', '#4b4233'))))
                    painter.setPen(QtGui.QPen(QtGui.QColor('#76664c'), .6))
                    painter.drawPolygon(QtGui.QPolygonF(points))
                offset = end+2
        for horizontal, length in ((True, self.width()), (False, self.height())):
            for offset in range(24, length-24, 9):
                depth = rng.randint(2, 12)
                shade = QtGui.QColor('#ba9a70' if rng.random() > .7 else '#0d1111')
                shade.setAlpha(rng.randint(45, 145))
                painter.setPen(QtGui.QPen(shade, rng.choice((1, 1, 2))))
                for opposite in (False, True):
                    x, y = (offset, depth) if horizontal else (depth, offset)
                    if opposite:
                        if horizontal: y = self.height()-depth
                        else: x = self.width()-depth
                    painter.drawLine(x, y, x+rng.randint(2, 7), y+rng.randint(-2, 2))
        for x, y, dx, dy in ((3,3,1,1),(self.width()-4,3,-1,1),(3,self.height()-4,1,-1),(self.width()-4,self.height()-4,-1,-1)):
            plate = QtGui.QPolygonF([QtCore.QPointF(x,y),QtCore.QPointF(x+31*dx,y),QtCore.QPointF(x+31*dx,y+7*dy),QtCore.QPointF(x+7*dx,y+31*dy),QtCore.QPointF(x,y+31*dy)])
            painter.setPen(QtGui.QPen(QtGui.QColor('#a29b82'), 1))
            painter.setBrush(QtGui.QColor('#353c37'))
            painter.drawPolygon(plate)
            painter.setBrush(QtGui.QColor('#acaa91'))
            painter.drawEllipse(QtCore.QPointF(x+8*dx,y+8*dy),2.5,2.5)


class FoundryTitleBar(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._variant = None
        self.set_variant('simulation')

    def set_variant(self, variant):
        if variant != self._variant:
            self._variant = variant
            self._art = QtGui.QPixmap(str(Path(__file__).parent / 'assets' / f'foundry-{variant}.png'))
            self.update()

    def paintEvent(self, event):
        if getattr(self.window(), '_theme_id', 'foundry') != 'foundry':
            return super().paintEvent(event)
        painter = QtGui.QPainter(self)
        paint_environment(self, painter, self._art)
        # Preserve the approved mark and readable window controls; fade into
        # the same scene, rather than ending the header in a solid strip.
        shade = QtGui.QLinearGradient(0, 0, 0, self.height())
        shade.setColorAt(0, QtGui.QColor(3, 7, 8, 190))
        shade.setColorAt(1, QtGui.QColor(3, 7, 8, 0))
        painter.fillRect(self.rect(), shade)
        shade = QtGui.QLinearGradient(0, 0, 720, 0)
        shade.setColorAt(0, QtGui.QColor(3, 7, 8, 245))
        shade.setColorAt(.7, QtGui.QColor(3, 7, 8, 220))
        shade.setColorAt(1, QtGui.QColor(3, 7, 8, 0))
        painter.fillRect(self.rect(), shade)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton and self.window().windowHandle():
            self.window().windowHandle().startSystemMove()
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.toggle_maximized()

    def toggle_maximized(self):
        window = self.window()
        window.showNormal() if window.isMaximized() else window.showMaximized()


class FoundryBackdrop(QtWidgets.QWidget):
    def __init__(self, parent=None, variant='background'):
        super().__init__(parent)
        self.setObjectName('foundryBackdrop')
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_OpaquePaintEvent)
        self._variant = None
        self.set_variant(variant)

    def set_variant(self, variant):
        if variant != self._variant:
            self._variant = variant
            self._art = QtGui.QPixmap(str(Path(__file__).parent / 'assets' / f'foundry-{variant}.png'))
            self.update()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        from .dpsfoundry_theme import THEMES
        theme = THEMES[getattr(self.window(), '_theme_id', 'foundry')]
        painter.fillRect(self.rect(), QtGui.QColor(theme.root))
        if theme.theme_id == 'foundry' and not self._art.isNull():
            paint_environment(self, painter, self._art)


def paint_environment(widget, painter, art):
    """One window-sized scene, sampled by each surface without restarting it."""
    painter.fillRect(widget.rect(), QtGui.QColor('#080e12'))
    if art.isNull():
        return
    window = widget.window()
    origin = widget.mapTo(window, QtCore.QPoint(0, 0))
    size = art.size().scaled(window.size(), QtCore.Qt.AspectRatioMode.KeepAspectRatioByExpanding)
    target = QtCore.QRectF((window.width()-size.width())/2-origin.x(),
                         (window.height()-size.height())/2-origin.y(), size.width(), size.height())
    painter.setRenderHint(QtGui.QPainter.RenderHint.SmoothPixmapTransform)
    painter.drawPixmap(target, art, QtCore.QRectF(art.rect()))
    painter.fillRect(widget.rect(), QtGui.QColor(8, 12, 14, 90))


def soft_glow(widget, color='#ecab58', blur=15):
    glow = QtWidgets.QGraphicsDropShadowEffect(widget)
    glow.setOffset(0, 0)
    glow.setBlurRadius(blur)
    shade = QtGui.QColor(color)
    shade.setAlpha(150)
    glow.setColor(shade)
    widget.setGraphicsEffect(glow)
