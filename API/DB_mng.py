import os
import psycopg2


class DB_handler:

    def __init__(self):
        self.db = psycopg2.connect(
            host=os.environ.get('DB_HOST', 'localhost'),
            dbname=os.environ.get('DB_NAME', 'mydb'),
            user=os.environ.get('DB_USER', 'admin'),
            password=os.environ.get('DB_PASSWORD', 'admin'),
            port=int(os.environ.get('DB_PORT', 5432))
        )
        self.cursor = self.db.cursor()

    def __del__(self):
        self.cursor.close()
        self.db.close()

    def execute(self, query, args={}):
        self.cursor.execute(query, args)
        row = self.cursor.fetchall()
        return row

    def commit(self):
        self.db.commit()

    def insert(self, schema, table, column, data):
        sql = "INSERT INTO %s.%s (%s) VALUES (%%s) ;"
        self.cursor.execute(
            sql % (schema, table, column),
            (data,)
        )
        self.db.commit()

    def read(self, schema, table, column):
        sql = "SELECT %s FROM %s.%s ;"
        try:
            self.cursor.execute(sql % (column, schema, table))
            result = self.cursor.fetchall()
        except Exception as e:
            result = None
            print(f"error while reading : {e}")
        return result

    def update(self, schema, table, column, value, condition_column, condition_value):
        sql = "UPDATE %s.%s SET %s = %%s WHERE %s = %%s ;"
        self.cursor.execute(
            sql % (schema, table, column, condition_column),
            (value, condition_value)
        )
        self.db.commit()

    def delete(self, schema, table, condition_column, condition_value):
        sql = "DELETE FROM %s.%s WHERE %s = %%s ;"
        self.cursor.execute(
            sql % (schema, table, condition_column),
            (condition_value,)
        )
        self.db.commit()
