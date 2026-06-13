import csv
import json
from pathlib import Path
from .errors import TableNotFoundError, DuplicateTableError, InvalidStorageDataError
from .table import Table


class CsvDatabase:
    def __init__(self, directory="data_csv"):
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
            file.stem.replace('_schema', '') for file in self.directory.glob("*_schema.json")
            if file.is_file()
        ]

    def _table_exists(self, table_name):
        return self._get_csv_path(table_name).exists()

    def _load_table(self, table_name):
        csv_path = self._get_csv_path(table_name)
        schema_path = self._get_schema_path(table_name)

        if not csv_path.exists() or not schema_path.exists():
            raise TableNotFoundError(table_name)

        try:
            with schema_path.open("r", encoding="utf-8") as file:
                schema = json.load(file)
        except json.JSONDecodeError:
            raise InvalidStorageDataError("Файл схемы содержит некорректный JSON")

        try:
            with csv_path.open("r", encoding="utf-8", newline="") as file:
                reader = csv.DictReader(file)
                records = []
                for row in reader:
                    record = {}
                    for key, value in row.items():
                        if key == 'id':
                            record[key] = int(value)
                        elif key in schema['columns']:
                            try:
                                record[key] = int(value)
                            except ValueError:
                                record[key] = value
                    records.append(record)
        except csv.Error:
            raise InvalidStorageDataError("CSV файл содержит ошибки")

        table = Table(tuple(schema['columns']), records)
        if 'next_id' in schema:
            table.next_id = schema['next_id']
        if 'indexes' in schema:
            table.indexes = schema['indexes']
        return table

    def _save_table(self, table_name, table):
        csv_path = self._get_csv_path(table_name)
        schema_path = self._get_schema_path(table_name)

        schema = {
            'columns': list(table.columns),
            'next_id': table.next_id,
            'indexes': table.indexes
        }

        with schema_path.open("w", encoding="utf-8") as file:
            json.dump(schema, file, ensure_ascii=False, indent=2)

        with csv_path.open("w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=['id'] + list(table.columns))
            writer.writeheader()
            for record in table.records:
                writer.writerow(record)

    def _get_csv_path(self, table_name):
        return self.directory / f"{table_name}.csv"

    def _get_schema_path(self, table_name):
        return self.directory / f"{table_name}_schema.json"