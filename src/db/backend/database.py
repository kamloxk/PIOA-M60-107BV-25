from abc import ABC, abstractmethod

from .errors import DuplicateTableError, TableNotFoundError


class Database(ABC):
    def create_table(self, table_name, columns):
        if self._table_exists(table_name):
            raise DuplicateTableError(table_name)
        self._save_table(table_name, self._create_table_instance(columns))

    def insert_record(self, table_name, record):
        table = self._load_table(table_name)
        record_id = table.insert_record(record)
        self._save_table(table_name, table)
        return record_id

    def select_records(self, table_name, **filters):
        table = self._load_table(table_name)
        return table.select_records(**filters)

    def update_record(self, table_name, record_id, data):
        table = self._load_table(table_name)
        updated = table.update_record(record_id, data)
        self._save_table(table_name, table)
        return updated

    def delete_record(self, table_name, record_id):
        table = self._load_table(table_name)
        deleted = table.delete_record(record_id)
        self._save_table(table_name, table)
        return deleted

    def create_index(self, table_name, column_name):
        table = self._load_table(table_name)
        table.create_index(column_name)
        self._save_table(table_name, table)

    def list_tables(self):
        return self._get_table_names()

    @abstractmethod
    def _table_exists(self, table_name):
        pass

    @abstractmethod
    def _load_table(self, table_name):
        pass

    @abstractmethod
    def _save_table(self, table_name, table):
        pass

    @abstractmethod
    def _get_table_names(self):
        pass

    @abstractmethod
    def _create_table_instance(self, columns):
        pass