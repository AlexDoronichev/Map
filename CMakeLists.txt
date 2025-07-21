cmake_minimum_required(VERSION 3.25.1)

add_executable(Map main.py)
message(STATUS  ${CMAKE_PREFIX_PATH})
message(STATUS  ${CMAKE_PYTHON_COMPILER})
set(CMAKE_PYTHON_COMPILER "/home/administrator/environment/bin/python3")
message(STATUS  ${CMAKE_PREFIX_PATH})
message(STATUS  ${CMAKE_PYTHON_COMPILER})
project(Map PYTHON)

find_package(Python COMPONENTS Interpreter Development REQUIRED)

set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)
set(CMAKE_AUTOUIC ON)

#find_package(Qt5 COMPONENTS Widgets REQUIRED)



message(STATUS  ${CMAKE_MODULE_PATH})
set(CMAKE_MODULE_PATH "/usr/lib/x86_64-linux-gnu/cmake")
message(STATUS  ${CMAKE_MODULE_PATH})
#set (Qt5_DIR "/usr/lib/x86_64-linux-gnu/cmake")
find_package(Qt5 COMPONENTS Core Gui Widgets REQUIRED)


# Добавляем пути к исходным файлам
target_sources(Map PRIVATE
	DB_controller.py
	Map.pyproject
	Map.pyproject.user
	Mark.py
	main.py
	main_mark.png
	mark.png
	moscow_map.jpg
)

# Добавляем необходимые библиотеки
target_link_libraries(Map PRIVATE
        Qt::Gui
        Qt::Core
        Qt::Widgets
)
