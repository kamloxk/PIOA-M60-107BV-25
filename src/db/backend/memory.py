from src.db.backend.errors import (
    TableNotFoundError,
    RecordNotFoundError,
    DuplicateTableError,
    ValidationError
)


class Record:
    def __init__(self, record_id, data):
        self.id = record_id
        self.data = data
    
    def to_dict(self):
        result = {'id': self.id}
        result.update(self.data)
        return result
    
    def update(self, new_data):
        self.data.update(new_data)


class Table:
    def __init__(self, name):
        self.name = name
        self.records = {}
        self.next_id = 1
    
    def create(self, data):
        record = Record(self.next_id, data)
        self.records[self.next_id] = record
        self.next_id += 1
        return record
    
    def select(self, filters=None, sort_by=None, sort_order='asc'):
        result = []
        for record in self.records.values():
            if filters is None:
                result.append(record)
            else:
                match = True
                for key, value in filters.items():
                    if key not in record.data or record.data[key] != value:
                        match = False
                        break
                if match:
                    result.append(record)
        
        if sort_by and result:
            reverse = sort_order == 'desc'
            try:
                result.sort(key=lambda r: r.data.get(sort_by, ''), reverse=reverse)
            except TypeError:
                result.sort(key=lambda r: str(r.data.get(sort_by, '')), reverse=reverse)
        
        return [r.to_dict() for r in result]
    
    def update(self, record_id, new_data):
        if record_id not in self.records:
            raise RecordNotFoundError(record_id)
        self.records[record_id].update(new_data)
        return self.records[record_id]
    
    def delete(self, record_id):
        if record_id not in self.records:
            raise RecordNotFoundError(record_id)
        return self.records.pop(record_id)
    
    def count(self):
        return len(self.records)


class Database:
    def __init__(self):
        self.tables = {}
    
    def create_table(self, table_name):
        if table_name in self.tables:
            raise DuplicateTableError(table_name)
        self.tables[table_name] = Table(table_name)
        return self.tables[table_name]
    
    def get_table(self, table_name):
        if table_name not in self.tables:
            raise TableNotFoundError(table_name)
        return self.tables[table_name]
    
    def list_tables(self):
        return list(self.tables.keys())
    
    def create_record(self, table_name, data):
        table = self.get_table(table_name)
        return table.create(data)
    
    def select_records(self, table_name, filters=None, sort_by=None, sort_order='asc'):
        table = self.get_table(table_name)
        return table.select(filters, sort_by, sort_order)
    
    def update_record(self, table_name, record_id, data):
        table = self.get_table(table_name)
        return table.update(record_id, data)
    
    def delete_record(self, table_name, record_id):
        table = self.get_table(table_name)
        return table.delete(record_id)