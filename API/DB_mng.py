import psycopg2


class DB_handler:
        
    def __init__(self):
        self.db = psycopg2.connect(host='localhost', dbname='mydb',user='admiv',password='admin',port=5432)

        self.cursor = self.db.cursor()

    def __del__(self):
        self.db.close()
        self.cursor.close()

    def execute(self,query,args={}):
        self.cursor.execute(query,args)
        row = self.cursor.fetchall()
        return row

    def commit(self):
        self.cursor.commit()

    

    def insert(self, schema, table, colum, data): # create
        sql = f" INSERT INTO {schema}.{table}({colum}) VALUES ('{data}') ;"
        try:
            self.cursor.execute(sql)
            self.db.commit()
        except Exception as e:
            print(f"error while inserting : {e}")



    def read(self, schema, table, colum): #read
        sql = f" SELECT {colum} from {schema}.{table} ;"
        try:
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
        except Exception as e:
            result = f"error while reading : {e}"
            print(result)
        finally:
            return result
        


    def update(self, schema, table, colum, value, condition): #update
        sql = f" UPDATE {schema}.{table} SET {colum}='{value}' WHERE {colum}='{condition}' ;"
        try:
            self.cursor.execute(sql)
            self.db.commit()
        except Exception as e:
            print(f"error while updating : {e}")


    
    def delete(self, schema, table, condition): # delete
        sql = f" DELETE FROM {schema}.{table} WHERE ('{condition}') ;"
        try:
            self.cursor.execute(sql)
            self.db.commit()
        except Exception as e:
            print(f"error while deleting : {e}")
    
