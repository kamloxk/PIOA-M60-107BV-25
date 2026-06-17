import json
from pathlib import Path
from .errors import TableNotFoundError, DuplicateTableError, InvalidStorageDataError
from .table import Table


class FileDatabase:
    def __init__(self, directory="data"):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)

    def create_table(self, table_name, columns):
        if self._table_exists(table_name):
            raise DuplicateTableError(table_name)
        table = Table(columns)
        self._save_table(table_name, table)

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
        if not self.directory.exists():
            return []
        return [
            file.stem for file in self.directory.glob("*.json")
            if file.is_file()
        ]

    def sort_records(self, table_name, column_name, order='asc'):
        table = self._load_table(table_name)
        return table.sort_records(column_name, order)

    def _table_exists(self, table_name):
        return self._get_table_path(table_name).exists()

    def _load_table(self, table_name):
        table_path = self._get_table_path(table_name)
        if not table_path.exists():
            raise TableNotFoundError(table_name)

        try:
            with table_path.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except json.JSONDecodeError:
            raise InvalidStorageDataError("Файл содержит некорректный JSON")

        return self._deserialize_table(data)

    def _save_table(self, table_name, table):
        table_path = self._get_table_path(table_name)
        with table_path.open("w", encoding="utf-8") as file:
            json.dump(
                self._serialize_table(table),
                file,
                ensure_ascii=False,
                indent=2,
            )

    def _get_table_path(self, table_name):
        return self.directory / f"{table_name}.json"

    def _serialize_table(self, table):
        return {
            "columns": list(table.columns),
            "records": [record.copy() for record in table.records],
            "next_id": table.next_id,
            "indexes": table.indexes
        }

    def _deserialize_table(self, data):
        if "columns" not in data or "records" not in data:
            raise InvalidStorageDataError("Файл имеет некорректную структуру")

        columns = tuple(data["columns"])
        records = data.get("records", [])
        table = Table(columns, records)
        if "next_id" in data:
            table.next_id = data["next_id"]
        if "indexes" in data:
            table.indexes = data["indexes"]
        return table