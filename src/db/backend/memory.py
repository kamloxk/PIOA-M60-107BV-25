from .errors import TableNotFoundError, DuplicateTableError
from .table import Table


class MemoryDatabase:
    def __init__(self):
        self.tables = {}

    def create_table(self, table_name, columns):
        if table_name in self.tables:
            raise DuplicateTableError(table_name)
        self.tables[table_name] = Table(columns)

    def insert_record(self, table_name, record):
        if table_name not in self.tables:
            raise TableNotFoundError(table_name)
        return self.tables[table_name].insert_record(record)

    def select_records(self, table_name, **filters):
        if table_name not in self.tables:
            raise TableNotFoundError(table_name)
        return self.tables[table_name].select_records(**filters)

    def update_record(self, table_name, record_id, data):
        if table_name not in self.tables:
            raise TableNotFoundError(table_name)
        return self.tables[table_name].update_record(record_id, data)

    def delete_record(self, table_name, record_id):
        if table_name not in self.tables:
            raise TableNotFoundError(table_name)
        return self.tables[table_name].delete_record(record_id)

    def create_index(self, table_name, column_name):
        if table_name not in self.tables:
            raise TableNotFoundError(table_name)
        self.tables[table_name].create_index(column_name)

    def list_tables(self):
        return list(self.tables.keys())