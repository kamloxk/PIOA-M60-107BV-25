database = {
    'books': []
}

next_id = 1

def create_record(table_name, record_data):
    global next_id
    if table_name not in database:
        raise ValueError(f"Таблица {table_name} не существует")
    
    record = {'id': next_id}
    record.update(record_data)
    database[table_name].append(record)
    next_id += 1
    return record

def select_record(table_name, filters=None):
    if table_name not in database:
        raise ValueError(f"Таблица {table_name} не существует")
    
    if filters is None:
        return database[table_name].copy()
    
    result = []
    for record in database[table_name]:
        match = True
        for key, value in filters.items():
            if key not in record or record[key] != value:
                match = False
                break
        if match:
            result.append(record.copy())
    return result

def update_record(table_name, record_id, update_data):
    if table_name not in database:
        raise ValueError(f"Таблица {table_name} не существует")
    
    for record in database[table_name]:
        if record['id'] == record_id:
            record.update(update_data)
            return record
    raise ValueError(f"Запись с id {record_id} не найдена")

def delete_record(table_name, record_id):
    if table_name not in database:
        raise ValueError(f"Таблица {table_name} не существует")
    
    for i, record in enumerate(database[table_name]):
        if record['id'] == record_id:
            deleted = database[table_name].pop(i)
            return deleted
    raise ValueError(f"Запись с id {record_id} не найдена")

def get_all_tables():
    return list(database.keys())

def create_table(table_name, fields=None):
    if table_name in database:
        raise ValueError(f"Таблица {table_name} уже существует")
    database[table_name] = []
    return table_name