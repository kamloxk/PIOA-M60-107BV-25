from abc import ABC, abstractmethod


class Database(ABC):
    @abstractmethod
    def create_table(self, table_name, columns):
        pass

    @abstractmethod
    def insert_record(self, table_name, record):
        pass

    @abstractmethod
    def select_records(self, table_name, **filters):
        pass

    @abstractmethod
    def update_record(self, table_name, record_id, data):
        pass

    @abstractmethod
    def delete_record(self, table_name, record_id):
        pass

    @abstractmethod
    def create_index(self, table_name, column_name):
        pass

    @abstractmethod
    def list_tables(self):
        pass

    @abstractmethod
    def sort_records(self, table_name, column_name, order='asc'):
        pass