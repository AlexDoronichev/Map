# This Python file uses the following encoding: utf-8
import sys

from PySide2.QtGui import QPixmap, QImage
from PySide2.QtCore import Qt, QPointF, QDir
from PySide2.QtWidgets import (
    QGraphicsView,
    QGraphicsScene,
    QGraphicsPixmapItem,
    QGraphicsItem,
)

class Mark(QGraphicsPixmapItem):
    main_mark = None
    mark_selected = False
    image_path_main_mark = "/main_mark.png"
    image_path_mark = "/mark.png"
    singalManager = None

    def __init__(self, coords: QPointF, is_main: bool):
        super().__init__()
        _image_path = None
        if is_main:
            _image_path = Mark.image_path_main_mark
        else:
            _image_path = Mark.image_path_mark
        self.setImage(_image_path)

        self.setPos(round(coords.x()), round(coords.y()))

        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges);

        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True) # Разрешаем перемещение
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True) # Разрешаем выделение

    def setImage(self, _image_path: str):
        _path = QDir.currentPath() + _image_path
        _qImage = QImage(_path)
        if _qImage.isNull():
            print("Не удалось загрузить изображение")
            sys.exit(1)
        self.pixmap = QPixmap.fromImage(_qImage)
        self.setOffset(QPointF(-self.pixmap.width() / 2, -self.pixmap.height()))
        self.setPixmap(self.pixmap)

    def itemChange(self, change, value):
        if (change == QGraphicsItem.ItemPositionHasChanged or change == QGraphicsItem.ItemSceneHasChanged):
            if self == self.main_mark and self.scene() and Mark.singalManager:
                Mark.singalManager.main_mark_pos_changed.emit(self.pos())
            return value;
        return super().itemChange(change, value)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            Mark.mark_selected = True
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            Mark.mark_selected = False
            if Mark.main_mark:
                if self != Mark.main_mark:
                    tmp_pos = Mark.main_mark.pos()
                    Mark.main_mark.setPos(self.pos())
                    self.setPos(tmp_pos)
            else:
                self.setImage(Mark.image_path_main_mark)
                Mark.main_mark = self
        elif event.button() == Qt.RightButton:
            if self == Mark.main_mark:
                Mark.main_mark = None
            if self.scene():
                self.scene().removeItem(self)

        super().mouseReleaseEvent(event)

