class DatabaseError(Exception):
    pass

class TableNotFoundError(DatabaseError):
    def __init__(self, table_name):
        super().__init__(f"Таблица '{table_name}' не найдена")

class RecordNotFoundError(DatabaseError):
    def __init__(self, record_id):
        super().__init__(f"Запись с ID {record_id} не найдена")

class DuplicateTableError(DatabaseError):
    def __init__(self, table_name):
        super().__init__(f"Таблица '{table_name}' уже существует")

class MissingColumnError(DatabaseError):
    def __init__(self, column_name):
        super().__init__(f"Отсутствует поле '{column_name}'")

class UnknownColumnError(DatabaseError):
    def __init__(self, column_name):
        super().__init__(f"Поле '{column_name}' не определено")

class InvalidStorageDataError(DatabaseError):
    pass