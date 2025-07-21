# This Python file uses the following encoding: utf-8
import psycopg2

from PySide2.QtCore import QPointF
from PySide2.QtWidgets import QMessageBox

class DB_controller:
    map_points_db_conn = None

    def __init__(self):
        pass

    def connect():
        try:
            DB_controller.map_points_db_conn = psycopg2.connect(
                host="0.0.0.0",
                port="5432",
                database="test_db",
                user="test_user1",
                password="123"
            )
        except psycopg2.Error as e:
            print(f"Ошибка подключения к базе данных: {e}")

    def create_table():
        DB_controller.connect()

        try:
            cursor = DB_controller.map_points_db_conn.cursor()

            create_table_query = """
            CREATE TABLE IF NOT EXISTS Points (
                id SERIAL PRIMARY KEY,
                longitude NUMERIC(10, 6) NOT NULL,
                latitude NUMERIC(10, 6) NOT NULL
            );
            """

            cursor.execute(create_table_query)
            DB_controller.map_points_db_conn.commit()
            cursor.close()

        except Exception as e:
            print(f"Ошибка при создании таблицы: {e}")

        finally:
            if DB_controller.map_points_db_conn:
                DB_controller.map_points_db_conn.close()

    def add_entry(coords: QPointF):
        entry_added = False
        DB_controller.connect()

        try:
            cursor = DB_controller.map_points_db_conn.cursor()
            query = "SELECT EXISTS (SELECT 1 FROM Points WHERE longitude = %s AND latitude = %s)"
            cursor.execute(query, (coords.x(), coords.y()))
            result = cursor.fetchall()
            is_point_exists = result[0][0]
            if is_point_exists is True:
                message_template = "Точка ({x}, {y}) уже есть в БД."
            else:
                entry_added = True
                query = "INSERT INTO Points (longitude, latitude) VALUES (%s, %s)"
                cursor.execute(query, (coords.x(), coords.y()))
                DB_controller.map_points_db_conn.commit()
                message_template = "Точка ({x}, {y}) добавлена в БД."
            cursor.close()
            message = message_template.format(x=coords.x(), y=coords.y())
            QMessageBox.information(None, "Сообщение", message)

        except psycopg2.Error as e:
            print(f"Ошибка при выполнении запроса: {e}")

        finally:
            if DB_controller.map_points_db_conn:
                DB_controller.map_points_db_conn.close()

    def get_all_entries():
        entries = []
        DB_controller.connect()

        try:
            cursor = DB_controller.map_points_db_conn.cursor()
            query = "SELECT * FROM Points"
            cursor.execute(query)
            result = cursor.fetchall()
            for row in result:
                entries.append((row[1], row[2]))
            cursor.close()

        except psycopg2.Error as e:
            print(f"Ошибка при выполнении запроса: {e}")

        finally:
            if DB_controller.map_points_db_conn:
                DB_controller.map_points_db_conn.close()

        return entries

    def clear_table():
        DB_controller.connect()

        try:
            cursor = DB_controller.map_points_db_conn.cursor()
            query = "DELETE FROM Points"
            cursor.execute(query)
            DB_controller.map_points_db_conn.commit()
            cursor.close()
            QMessageBox.information(None, "Сообщение", "База данных очищена.")

        except psycopg2.Error as e:
            print(f"Ошибка при выполнении запроса: {e}")

        finally:
            if DB_controller.map_points_db_conn:
                DB_controller.map_points_db_conn.close()
