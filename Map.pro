TARGET = Map

TEMPLATE = app

QT += core gui widgets

PYTHON_EXECUTABLE = /home/administrator/environment/bin/python3
PYSIDE_VERSION = 2

#INCLUDEPATH += $$[QT_INSTALL_HEADERS]/QtGui

SOURCES += \
    main.py \
    Mark.py \
    DB_controller.py

HEADERS += \
    Map.pyproject

RESOURCES += \
    main_mark.png \
    mark.png \
    moscow_map.jpg

# Default rules for deployment.
qnx: target.path = /tmp/$${TARGET}/bin
else: unix:!android: target.path = /opt/$${TARGET}/bin
!isEmpty(target.path): INSTALLS += target
