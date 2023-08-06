import sqlite3

class Database:

    def __init__(self, name:str):
        self.file_name = name
        self.db = sqlite3.connect(f"./{name if '.db' in name else name+'.db'}") 
        self.c = self.db.cursor()

        self.tables = {}
        self.auto_commit = True

        self.get_tables()

    def create_table(self, table_name, columns):
        if isinstance(columns, (tuple, list)):
            columns = ', '.join(columns)
            
        elif isinstance(columns, dict):
            for v in columns.values():
                 for w in v.split(' '):
                    if w not in ['INTEGER', 'TEXT', 'REAL', 'BLOB', 'PRIMARY KEY']:
                        raise RuntimeError('Invalid column discriptions.') 
                        
            columns = ', '.join(f'{k} {v}' for k, v in columns.items())
        else:
            raise RuntimeError('Columns must be a dictionary, tuple or list')
        
        self.c.execute("CREATE TABLE IF NOT EXISTS {} ({})".format(table_name, columns))
        self.commit(False)

        self.get_tables()

    def delete_table(self, table_name):
        self.c.execute("DROP TABLE IF EXISTS {}".format(table_name))
        self.commit(False)

    def clear_table(self, table_name):
        self.c.execute("DELETE FROM {}".format(table_name))
        self.commit(False)

    def select(self, table_name, selected='*', where='', size='*', separator='AND'):

        if selected != '*' and not isinstance(selected, (list, tuple)):
            raise RuntimeError('Selected fields must be provided as a list or tuple')

        if where != '':
            if not isinstance(where, dict):
                raise RuntimeError("WHERE expression must be provided as a dictionary.")

            where = 'WHERE' + separator.join(["{} = {}".format(k, v if not isinstance(v, str) else f'\"{v}\"') for k, v in where.items()])

        selected = ', '.join(selected)
        size = '*' if size == '*' or not isinstance(size, int) else int(size)

        self.c.execute(f"SELECT {selected} FROM {table_name} {where}")
        
        if size == '*':
            return self.c.fetchall()
        elif size == 1:
            return self.c.fetchone()
        else:
            return self.c.fetchmany(size)

    def insert(self, table_name, information):

        columns = ''
        if isinstance(information, dict):
            columns = "(" + ', '.join(list(information.keys())) + ")"
            information = information.values()
        elif not isinstance(information, (list, tuple)):
            raise RuntimeError("Information must be provided as a list, tuple or dictionary.")

        q = ','.join(['?' for _ in information]) 

        self.c.execute(f"INSERT INTO {table_name} {columns} values({q})", tuple(information))
        self.commit(False)

    def update(self, table_name, information, where, separator='AND'):
        if not isinstance(information, dict):
            raise RuntimeError("Information must be provided as a dictionary.")

        columns = ', '.join([f"{k}=:{k}" for k in information.keys()])
        where_c = separator.join([f" {k}=:{k} " for k in where])
        information.update(where)

        self.c.execute(f"UPDATE {table_name} SET {columns} WHERE {where_c}", information)
        self.commit(False)

    def delete(self, table_name, where, separator='AND'):
        if not isinstance(where, dict):
            raise RuntimeError("WHERE expression must be provided as a dictionary.")
        
        where = " WHERE " + f" {separator} ".join(self.__where(where)) if where else ''
        self.c.execute(f"DELETE FROM {table_name} WHERE {where}")
        self.commit(False)

    def get_count(self, table_name, where='', separator='AND'):
        
        if not isinstance(where, dict) and where != '':
            raise TypeError('Where clause must be a dictionary.')

        where = " WHERE " + f" {separator} ".join(self.__where(where)) if where else ''
            
        self.c.execute(f"SELECT COUNT(*) FROM {table_name}{where}")
        return self.c.fetchone()[0]

    def if_exists(self, table_name, where='', separator='AND'):
        if not isinstance(where, dict) and where != '':
            raise TypeError('Where clause must be a dictionary.')

        where = " WHERE " + f" {separator} ".join(self.__where(where)) if where else ''

        self.c.execute(f'SELECT EXISTS(SELECT 1 FROM {table_name}{where})')
        return True if self.c.fetchone()[0] else False

    def initiate_transaction(self):
        self.auto_commit = False

    def rollback(self):
        self.db.rollback()
        self.auto_commit = True

    def execute(self, command):
        self.c.execute(command)

    def close(self):
        self.db.close()

    def commit(self, o=True):

        if self.auto_commit or o:
            self.db.commit()
            if not self.auto_commit: self.auto_commit = True

    def get_tables(self):

        self.c.execute('SELECT name FROM sqlite_master WHERE type="table"')
        tables = self.c.fetchall()

        self.tables = {table[0]: self.get_table_structure(table[0]) for table in tables}
        return self.tables

    def get_table_structure(self, table_name):
        c = self.c.execute(f'SELECT * FROM {table_name}')
        c = [i[0] for i in c.description]
        return c

    def __where(self, where):
        where_c = []
        for k, v in where.items():
            if isinstance(v, (tuple, list)):
                for i in v:
                    where_c.append('{} = {}'.format(k, i if not isinstance(i, str) else f'\"{i}\"'))
            else:
                where_c.append('{} = {}'.format(k, v if not isinstance(v, str) else f"\"{v}\""))

        return where_c