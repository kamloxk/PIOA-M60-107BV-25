from src.db.backend.file import FileDatabase
from src.db.backend.csv_db import CsvDatabase
from src.db.backend.memory import MemoryDatabase
from src.db.backend.errors import (
    TableNotFoundError,
    RecordNotFoundError,
    DuplicateTableError,
    MissingColumnError,
    UnknownColumnError
)


class Menu:
    def __init__(self, title, options):
        self.title = title
        self.options = options

    def display(self):
        print(f"\n=== {self.title} ===")
        for key, value in self.options.items():
            print(f"{key}. {value}")

    def get_choice(self):
        try:
            return input("Выберите действие: ").strip()
        except EOFError:
            return "0"


class LibraryApp:
    def __init__(self, database=None):
        self.db = database
        if 'books' not in self.db.list_tables():
            self.db.create_table('books', ('title', 'author', 'year', 'genre'))

        self.main_menu = Menu(
            "БАЗА ДАННЫХ БИБЛИОТЕКИ",
            {
                "1": "Показать все книги",
                "2": "Найти книгу",
                "3": "Добавить книгу",
                "4": "Изменить книгу",
                "5": "Удалить книгу",
                "6": "Сортировать книги",
                "7": "Создать индекс",
                "8": "Создать таблицу",
                "9": "Показать таблицы",
                "0": "Выход"
            }
        )

    def run(self):
        while True:
            self.main_menu.display()
            choice = self.main_menu.get_choice()

            if choice == "1":
                self.show_all_books()
            elif choice == "2":
                self.find_book()
            elif choice == "3":
                self.add_book()
            elif choice == "4":
                self.edit_book()
            elif choice == "5":
                self.remove_book()
            elif choice == "6":
                self.sort_books()
            elif choice == "7":
                self.create_index_ui()
            elif choice == "8":
                self.create_table_ui()
            elif choice == "9":
                self.show_tables()
            elif choice == "0":
                print("До свидания!")
                break
            else:
                print("Неверный выбор")

    def print_books(self, books):
        if not books:
            print("Книги не найдены")
            return
        print("\n--- СПИСОК КНИГ ---")
        for book in books:
            print(f"ID: {book['id']}")
            print(f"Название: {book['title']}")
            print(f"Автор: {book['author']}")
            print(f"Год: {book['year']}")
            print(f"Жанр: {book['genre']}")
            print()

    def get_input(self, prompt):
        try:
            return input(prompt).strip()
        except EOFError:
            return ""

    def get_number(self, prompt):
        while True:
            try:
                return int(input(prompt).strip())
            except ValueError:
                print("Ошибка: введите число")
            except EOFError:
                return None

    def show_all_books(self):
        try:
            books = self.db.select_records('books')
            self.print_books(books)
        except TableNotFoundError as e:
            print(f"Ошибка: {e}")

    def find_book(self):
        print("\n--- ПОИСК КНИГИ ---")
        print("1. По названию")
        print("2. По автору")
        print("3. По году")
        print("4. По жанру")

        choice = self.get_number("Выбор: ")
        filters = {}

        if choice == 1:
            value = self.get_input("Введите название: ")
            if value:
                filters['title'] = value
        elif choice == 2:
            value = self.get_input("Введите автора: ")
            if value:
                filters['author'] = value
        elif choice == 3:
            value = self.get_number("Введите год: ")
            if value:
                filters['year'] = value
        elif choice == 4:
            value = self.get_input("Введите жанр: ")
            if value:
                filters['genre'] = value
        else:
            print("Неверный выбор")
            return

        try:
            books = self.db.select_records('books', **filters)
            self.print_books(books)
        except TableNotFoundError as e:
            print(f"Ошибка: {e}")

    def add_book(self):
        print("\n--- ДОБАВЛЕНИЕ КНИГИ ---")

        title = self.get_input("Название: ")
        if not title:
            print("Ошибка: название обязательно")
            return

        author = self.get_input("Автор: ")
        if not author:
            print("Ошибка: автор обязателен")
            return

        year = self.get_number("Год издания: ")
        if year is None:
            print("Ошибка: год обязателен")
            return

        genre = self.get_input("Жанр: ")
        if not genre:
            print("Ошибка: жанр обязателен")
            return

        try:
            book_id = self.db.insert_record('books', {
                'title': title,
                'author': author,
                'year': year,
                'genre': genre
            })
            print(f"Книга добавлена с ID: {book_id}")
        except (TableNotFoundError, MissingColumnError, UnknownColumnError) as e:
            print(f"Ошибка: {e}")

    def edit_book(self):
        print("\n--- ИЗМЕНЕНИЕ КНИГИ ---")

        book_id = self.get_number("Введите ID книги: ")
        if book_id is None:
            return

        print("Что изменить?")
        print("1. Название")
        print("2. Автор")
        print("3. Год")
        print("4. Жанр")

        choice = self.get_number("Выбор: ")

        if choice == 1:
            field = 'title'
            new_value = self.get_input("Новое название: ")
        elif choice == 2:
            field = 'author'
            new_value = self.get_input("Новый автор: ")
        elif choice == 3:
            field = 'year'
            new_value = self.get_number("Новый год: ")
        elif choice == 4:
            field = 'genre'
            new_value = self.get_input("Новый жанр: ")
        else:
            print("Неверный выбор")
            return

        if new_value is None or new_value == "":
            print("Ошибка: значение не может быть пустым")
            return

        try:
            self.db.update_record('books', book_id, {field: new_value})
            print("Книга обновлена")
        except (TableNotFoundError, RecordNotFoundError, UnknownColumnError) as e:
            print(f"Ошибка: {e}")

    def remove_book(self):
        print("\n--- УДАЛЕНИЕ КНИГИ ---")

        book_id = self.get_number("Введите ID книги: ")
        if book_id is None:
            return

        try:
            deleted = self.db.delete_record('books', book_id)
            print(f"Книга '{deleted['title']}' удалена")
        except (TableNotFoundError, RecordNotFoundError) as e:
            print(f"Ошибка: {e}")

    def sort_books(self):
        print("\n--- СОРТИРОВКА КНИГ ---")
        print("По какому полю сортировать?")
        print("1. Название")
        print("2. Автор")
        print("3. Год")
        print("4. Жанр")

        field_choice = self.get_number("Выбор: ")
        fields = {1: 'title', 2: 'author', 3: 'year', 4: 'genre'}

        if field_choice not in fields:
            print("Неверный выбор")
            return

        sort_by = fields[field_choice]

        print("Порядок сортировки?")
        print("1. По возрастанию")
        print("2. По убыванию")

        order_choice = self.get_number("Выбор: ")
        order = 'asc' if order_choice == 1 else 'desc'

        try:
            books = self.db.select_records('books')
            if sort_by and books:
                reverse = order == 'desc'
                try:
                    books.sort(key=lambda b: b.get(sort_by, ''), reverse=reverse)
                except TypeError:
                    books.sort(key=lambda b: str(b.get(sort_by, '')), reverse=reverse)
            self.print_books(books)
        except TableNotFoundError as e:
            print(f"Ошибка: {e}")

    def create_index_ui(self):
        print("\n--- СОЗДАНИЕ ИНДЕКСА ---")
        print("По какому полю создать индекс?")
        print("1. Название")
        print("2. Автор")
        print("3. Год")
        print("4. Жанр")

        choice = self.get_number("Выбор: ")
        fields = {1: 'title', 2: 'author', 3: 'year', 4: 'genre'}

        if choice not in fields:
            print("Неверный выбор")
            return

        column = fields[choice]
        try:
            self.db.create_index('books', column)
            print(f"Индекс по полю '{column}' создан")
        except (TableNotFoundError, UnknownColumnError) as e:
            print(f"Ошибка: {e}")

    def create_table_ui(self):
        print("\n--- СОЗДАНИЕ ТАБЛИЦЫ ---")
        name = self.get_input("Имя таблицы: ")
        if not name:
            print("Ошибка: имя не может быть пустым")
            return
        try:
            self.db.create_table(name, ('field1', 'field2'))
            print(f"Таблица '{name}' создана")
        except DuplicateTableError as e:
            print(f"Ошибка: {e}")

    def show_tables(self):
        print("\n--- ТАБЛИЦЫ ---")
        for table in self.db.list_tables():
            print(f"- {table}")


def create_database():
    print("Выберите тип базы данных:")
    print("1. In-memory (временная)")
    print("2. File database (JSON)")
    print("3. CSV database")

    choice = input("Введите номер: ").strip()
    if choice == "2":
        return FileDatabase()
    elif choice == "3":
        return CsvDatabase()
    else:
        return MemoryDatabase()


def main():
    db = create_database()
    app = LibraryApp(database=db)
    app.run()