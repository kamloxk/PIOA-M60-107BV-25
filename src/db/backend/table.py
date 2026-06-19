from .errors import MissingColumnError, UnknownColumnError, RecordNotFoundError


class Table:
    def __init__(self, columns, records=None):
        self.columns = columns
        self.records = []
        self.next_id = 1
        self.indexes = {}

        if records is not None:
            for record in records:
                if 'id' in record and record['id'] >= self.next_id:
                    self.next_id = record['id'] + 1
                self.records.append(record)

    def create_index(self, column_name):
        if column_name not in self.columns:
            raise UnknownColumnError(column_name)
        
        self.indexes[column_name] = {}
        for record in self.records:
            value = record.get(column_name)
            if value not in self.indexes[column_name]:
                self.indexes[column_name][value] = []
            self.indexes[column_name][value].append(record['id'])

    def insert_record(self, record):
        # Проверяем, что все обязательные поля присутствуют
        for col in self.columns:
            if col not in record:
                raise MissingColumnError(col)

        # Проверяем, что нет лишних полей
        for col in record:
            if col not in self.columns and col != 'id':
                raise UnknownColumnError(col)

        # Если id задан явно — проверяем уникальность и обновляем next_id
        if 'id' in record:
            for existing in self.records:
                if existing.get('id') == record['id']:
                    raise ValueError(f"Запись с ID {record['id']} уже существует")
            if record['id'] >= self.next_id:
                self.next_id = record['id'] + 1
        else:
            # Если id не задан — генерируем новый
            record = {'id': self.next_id, **record}
            self.next_id += 1

        self.records.append(record.copy())

        # Обновляем индексы
        for column_name in self.indexes:
            value = record.get(column_name)
            if value not in self.indexes[column_name]:
                self.indexes[column_name][value] = []
            self.indexes[column_name][value].append(record['id'])

        return record['id']

    def select_records(self, **filters):
        for key in filters:
            if key not in self.columns and key != 'id':
                raise UnknownColumnError(key)

        if not filters:
            return [record.copy() for record in self.records]

        for key in filters:
            if key in self.indexes:
                value = filters[key]
                if value in self.indexes[key]:
                    candidate_ids = self.indexes[key][value]
                    result = []
                    for record in self.records:
                        if record['id'] in candidate_ids:
                            match = True
                            for filter_key, filter_value in filters.items():
                                if record.get(filter_key) != filter_value:
                                    match = False
                                    break
                            if match:
                                result.append(record.copy())
                    return result
                return []

        result = []
        for record in self.records:
            match = True
            for key, value in filters.items():
                if record.get(key) != value:
                    match = False
                    break
            if match:
                result.append(record.copy())

        return result

    def update_record(self, record_id, new_data):
        for record in self.records:
            if record.get('id') == record_id:
                for col in new_data:
                    if col not in self.columns and col != 'id':
                        raise UnknownColumnError(col)

                for column_name in self.indexes:
                    if column_name in new_data:
                        old_value = record.get(column_name)
                        new_value = new_data[column_name]
                        if old_value in self.indexes[column_name]:
                            self.indexes[column_name][old_value].remove(record_id)
                            if not self.indexes[column_name][old_value]:
                                del self.indexes[column_name][old_value]
                        if new_value not in self.indexes[column_name]:
                            self.indexes[column_name][new_value] = []
                        self.indexes[column_name][new_value].append(record_id)

                record.update(new_data)
                return record.copy()
        raise RecordNotFoundError(record_id)

    def delete_record(self, record_id):
        for i, record in enumerate(self.records):
            if record.get('id') == record_id:
                for column_name in self.indexes:
                    value = record.get(column_name)
                    if value in self.indexes[column_name]:
                        self.indexes[column_name][value].remove(record_id)
                        if not self.indexes[column_name][value]:
                            del self.indexes[column_name][value]
                return self.records.pop(i)
        raise RecordNotFoundError(record_id)

    def count(self):
        return len(self.records)

    def sort_records(self, column_name, order='asc'):
        if column_name not in self.columns:
            raise UnknownColumnError(column_name)
        records_copy = [record.copy() for record in self.records]
        try:
            records_copy.sort(
                key=lambda x: x.get(column_name, ''),
                reverse=(order == 'desc')
            )
        except TypeError:
            records_copy.sort(
                key=lambda x: str(x.get(column_name, '')),
                reverse=(order == 'desc')
            )
        return records_copy