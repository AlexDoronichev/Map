# This Python file uses the following encoding: utf-8
import os
from pathlib import Path
import sys
#import py_main

from PySide2.QtGui import QPixmap, QImage, QTransform
from PySide2.QtCore import Qt, QPointF, QRectF, QDir, Signal, QObject
from PySide2.QtWidgets import (
    QApplication,
    QGraphicsView,
    QGraphicsScene,
    QGraphicsPixmapItem,
    QGraphicsItem,
    QLineEdit,
    QMainWindow,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QWidget,
    QMessageBox
)

from DB_controller import DB_controller
from Mark import Mark

max_scale = 2.0
min_scale = 0.5
max_latitude_up = 100 #55.914883
max_latitude_down = 0 #55.564660
max_longitude_left = 0 #37.360806
max_longitude_right = 100 #37.858518

class SignalManager(QObject):
    main_mark_pos_changed = Signal(QPointF)

    def __init__(self):
            super().__init__()

class MyMainWindow(QMainWindow):
    singalManager = SignalManager()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("My PySide2 App")
        self.setGeometry(100, 100, 800, 600) # x, y, width, height

        Mark.singalManager = self.singalManager

        # Sets table for Database
        DB_controller.create_table()

        # Sets layout for main window
        container_widget = QWidget()
        h_layout = QHBoxLayout()

        self.mapView = MapView()
        h_layout.addWidget(self.mapView)

        self.control_panel = QWidget()
        #self.control_panel.setStyleSheet("border: 1px solid black; padding: 0px;")
        h_layout.addWidget(self.control_panel)

        container_widget.setLayout(h_layout)
        self.setCentralWidget(container_widget)

        # Sets layout for latitude
        lat_line = QWidget()
        lat_layout = QHBoxLayout()
        lat_line.setLayout(lat_layout)
        self.latitude = QLineEdit("0")
        self.latitude.setFixedWidth(100);
        lat_layout.addWidget(QLabel("Широта"))
        lat_layout.addWidget(self.latitude)

        # Sets layout for longitude
        long_line = QWidget()
        long_layout = QHBoxLayout()
        long_line.setLayout(long_layout)
        self.longitude = QLineEdit("0")
        self.longitude.setFixedWidth(100);
        long_layout.addWidget(QLabel("Долгота"))
        long_layout.addWidget(self.longitude)

        # Sets buttons
        save_button = QPushButton("Сохранить точку")
        save_button.clicked.connect(self.on_save_button_click)
        clear_marks_buttons = QPushButton("Удалить все метки")
        clear_marks_buttons.clicked.connect(self.on_clear_marks_button_click)
        clear_db_button = QPushButton("Очистить базу данных")
        clear_db_button.clicked.connect(self.on_clear_db_button_click)
        load_points_button = QPushButton("Загрузить все точки из БД")
        load_points_button.clicked.connect(self.on_load_points_button_click)

        # Sets layout for control panel
        v_layout = QVBoxLayout()
        self.control_panel.setLayout(v_layout)
        v_layout.addWidget(QLabel("Координаты"))
        v_layout.addWidget(lat_line)
        v_layout.addWidget(long_line)
        v_layout.addWidget(save_button)
        v_layout.addWidget(clear_marks_buttons)
        v_layout.addWidget(clear_db_button)
        v_layout.addWidget(load_points_button)
        v_layout.addStretch()

        self.latitude.textEdited.connect(self.on_latitude_changed)
        self.longitude.textEdited.connect(self.on_longitude_changed)

        MyMainWindow.singalManager.main_mark_pos_changed.connect(self.set_geo_coords_from_map_pos)

    def get_geo_coords(self):
        return QPointF(float(self.longitude.text()), float(self.latitude.text()))

    def set_geo_coords(self, coords: QPointF):
        self.longitude.setText(str(round(coords.x(), 6)))
        self.latitude.setText(str(round(coords.y(), 6)))

    def set_geo_coords_from_map_pos(self, map_pos: QPointF):
        geo_coords = MapView.map_pos_to_geo_coords(map_pos, self.mapView.scene.sceneRect())
        self.set_geo_coords(geo_coords)

    def get_latitude_in_bounds(self, geo_y):
        if geo_y > max_latitude_up:
            geo_y = max_latitude_up
        if geo_y < max_latitude_down:
            geo_y = max_latitude_down
        return geo_y

    def get_longitude_in_bounds(self, geo_x):
        if geo_x > max_longitude_right:
            geo_x = max_longitude_right
        if geo_x < max_longitude_left:
            geo_x = max_longitude_left
        return geo_x

    def on_latitude_changed(self):
        geo_y = float(self.latitude.text())
        geo_x = float(self.longitude.text())
        geo_y = self.get_latitude_in_bounds(geo_y)

        geo_coords = QPointF(geo_x, geo_y)
        self.set_geo_coords(geo_coords)
        map_pos = MapView.geo_coords_to_map_pos(geo_coords, self.mapView.scene.sceneRect())

        if Mark.main_mark:
            Mark.main_mark.setPos(map_pos)
        else:
            Mark.main_mark = Mark(map_pos, true)

    def on_longitude_changed(self):
        geo_y = float(self.latitude.text())
        geo_x = float(self.longitude.text())
        geo_x = self.get_longitude_in_bounds(geo_x)

        geo_coords = QPointF(geo_x, geo_y)
        self.set_geo_coords(geo_coords)
        map_pos = MapView.geo_coords_to_map_pos(geo_coords, self.mapView.scene.sceneRect())

        if Mark.main_mark:
            Mark.main_mark.setPos(map_pos)
        else:
            Mark.main_mark = Mark(map_pos, true)

    def on_save_button_click(self):
        coords = self.get_geo_coords()
        coords.setX(self.get_longitude_in_bounds(coords.x()))
        coords.setY(self.get_latitude_in_bounds(coords.y()))
        DB_controller.add_entry(coords)

    def on_clear_marks_button_click(self):
        for item in self.mapView.scene.items():
            if isinstance(item, Mark):
                self.mapView.scene.removeItem(item)
            Mark.main_mark = None

    def on_clear_db_button_click(self):
        DB_controller.clear_table()

    def on_load_points_button_click(self):
        marks_added = 0
        points = DB_controller.get_all_entries()
        if points:
            for point in points:
                point_map_pos = MapView.geo_coords_to_map_pos(QPointF(point[0], point[1]), self.mapView.scene.sceneRect())
                is_on_map = False
                for item in self.mapView.scene.items():
                    if isinstance(item, Mark):
                        point_map_pos.setX(round(point_map_pos.x()))
                        point_map_pos.setY(round(point_map_pos.y()))
                        if point_map_pos == item.pos():
                            is_on_map = True
                            break
                if not is_on_map:
                   self.mapView.scene.addItem(Mark(point_map_pos, False))
                   marks_added += 1

            if marks_added == 0:
                QMessageBox.information(None, "Сообщение", "Все точки из базы данных уже отмечены на карте.")
            else:
                QMessageBox.information(None, "Сообщение", f"На карте отмечено {marks_added} точек.")
        else:
            QMessageBox.information(None, "Сообщение", "Нет сохранённых точек.")

class MapView(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.map_image = None
        #self.setDragMode(QGraphicsView.ScrollHandDrag)  # Включение режима перетаскивания
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        #self.setCursor(Qt.ArrowCursor)

        # Загрузка карты
        filePath = QDir.currentPath() + "/moscow_map.jpg";
        map_image = QImage(filePath)
        if map_image.isNull():
            print("Не удалось загрузить изображение")
            sys.exit(1)
        pixmap = QPixmap.fromImage(map_image)
        self.map_item = QGraphicsPixmapItem(pixmap)
        self.map_item.setPos(0, 0)
        self.scene.addItem(self.map_item)

        self.scale_factor = 1.0
        self.last_mouse_pos = None
        self.mouse_moving = False

    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            self.scale_factor *= 1.1
        else:
            self.scale_factor /= 1.1
        self.scale_factor = min(max_scale, self.scale_factor)
        self.scale_factor = max(min_scale, self.scale_factor)
        self.resetTransform()
        self.scale(self.scale_factor, self.scale_factor)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.last_mouse_pos = event.pos()
        if event.button() == Qt.MouseButton.MiddleButton:
            map_pos = self.scr_pos_to_map_pos(event.pos())
            vari = Mark(map_pos, False)
            self.scene.addItem(vari)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.last_mouse_pos:
            delta = event.pos() - self.last_mouse_pos
            if Mark.mark_selected:
                map_pos = self.scr_pos_to_map_pos(event.pos())
            else:
                self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
                self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
            self.last_mouse_pos = event.pos()
            self.mouse_moving = True

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.last_mouse_pos = None
            if self.mouse_moving:
                self.mouse_moving = False
            elif not Mark.mark_selected:
                map_pos = self.scr_pos_to_map_pos(event.pos())
                if not Mark.main_mark is None:
                    if not Mark.main_mark.scene():
                        self.scene.addItem(Mark.main_mark)
                    Mark.main_mark.setPos(map_pos)
                else:
                    vari = Mark(map_pos, True)
                    #print(vari)
                    #Mark.main_mark = 2
                    #print(Mark.mark_selected)
                    Mark.main_mark = vari
                    self.scene.addItem(Mark.main_mark)
                    #Mark.main_mark = Mark(map_pos, True)
                    #print(Mark.main_mark)
                    #self.scene.addItem(Mark.main_mark)
                    #self.scene.addItem(Mark(map_pos, True))

        super().mouseReleaseEvent(event)

    def scr_pos_to_map_pos(self, scrPos) -> QPointF:
        x = (self.horizontalScrollBar().value() + scrPos.x() - 10.0) / self.scale_factor
        y = (self.verticalScrollBar().value() + scrPos.y() - 10.0) / self.scale_factor
        return QPointF(x, y)

    @staticmethod
    def map_pos_to_geo_coords(map_pos: QPointF, scene_rect: QRectF) -> QPointF:
        map_pos.setY(scene_rect.height() - map_pos.y())
        geo_x = max_longitude_left + (max_longitude_right - max_longitude_left) * map_pos.x() / scene_rect.width()
        geo_y = max_latitude_down + (max_latitude_up - max_latitude_down) * map_pos.y() / scene_rect.height()
        return QPointF(geo_x, geo_y)

    @staticmethod
    def geo_coords_to_map_pos(geo_coords: QPointF, scene_rect: QRectF) -> QPointF:
        map_x = scene_rect.width() * (geo_coords.x() - max_longitude_left) / (max_longitude_right - max_longitude_left)
        map_y = scene_rect.height() * (geo_coords.y() - max_latitude_down) / (max_latitude_up - max_latitude_down)
        map_y = scene_rect.height() - map_y
        return QPointF(round(map_x), round(map_y))

if __name__ == '__main__':
    app = QApplication(sys.argv)

    mainWindow = MyMainWindow()
    mainWindow.show()

    sys.exit(app.exec_())
