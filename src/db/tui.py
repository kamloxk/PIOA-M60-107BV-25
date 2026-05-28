from src.db.backend.memory import (
    create_record, select_record, update_record, 
    delete_record, get_all_tables, create_table
)

def print_menu():
    print("\n=== БАЗА ДАННЫХ БИБЛИОТЕКИ ===")
    print("1. Показать все книги")
    print("2. Найти книгу")
    print("3. Добавить книгу")
    print("4. Изменить книгу")
    print("5. Удалить книгу")
    print("6. Создать новую таблицу")
    print("7. Показать все таблицы")
    print("0. Выход")

def print_books(books):
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

def get_input(prompt):
    try:
        return input(prompt).strip()
    except EOFError:
        return ""

def get_number_input(prompt):
    while True:
        try:
            return int(input(prompt).strip())
        except ValueError:
            print("Ошибка: введите число")
        except EOFError:
            return None

def show_all_books():
    try:
        books = select_record('books')
        print_books(books)
    except ValueError as e:
        print(f"Ошибка: {e}")

def find_book():
    print("\n--- ПОИСК КНИГИ ---")
    print("По каким параметрам искать?")
    print("1. По названию")
    print("2. По автору")
    print("3. По году")
    print("4. По жанру")
    
    choice = get_number_input("Выбор: ")
    
    filters = {}
    
    if choice == 1:
        title = get_input("Введите название: ")
        if title:
            filters['title'] = title
    elif choice == 2:
        author = get_input("Введите автора: ")
        if author:
            filters['author'] = author
    elif choice == 3:
        year = get_number_input("Введите год: ")
        if year:
            filters['year'] = year
    elif choice == 4:
        genre = get_input("Введите жанр: ")
        if genre:
            filters['genre'] = genre
    else:
        print("Неверный выбор")
        return
    
    try:
        books = select_record('books', filters)
        print_books(books)
    except ValueError as e:
        print(f"Ошибка: {e}")

def add_book():
    print("\n--- ДОБАВЛЕНИЕ КНИГИ ---")
    
    title = get_input("Название: ")
    if not title:
        print("Ошибка: название обязательно")
        return
    
    author = get_input("Автор: ")
    if not author:
        print("Ошибка: автор обязателен")
        return
    
    year = get_number_input("Год издания: ")
    if year is None:
        print("Ошибка: год обязателен")
        return
    
    genre = get_input("Жанр: ")
    if not genre:
        print("Ошибка: жанр обязателен")
        return
    
    try:
        book = create_record('books', {
            'title': title,
            'author': author,
            'year': year,
            'genre': genre
        })
        print(f"Книга добавлена с ID: {book['id']}")
    except ValueError as e:
        print(f"Ошибка: {e}")

def edit_book():
    print("\n--- ИЗМЕНЕНИЕ КНИГИ ---")
    
    book_id = get_number_input("Введите ID книги: ")
    if book_id is None:
        return
    
    print("Что изменить?")
    print("1. Название")
    print("2. Автор")
    print("3. Год")
    print("4. Жанр")
    
    choice = get_number_input("Выбор: ")
    
    if choice == 1:
        field = 'title'
        new_value = get_input("Новое название: ")
    elif choice == 2:
        field = 'author'
        new_value = get_input("Новый автор: ")
    elif choice == 3:
        field = 'year'
        new_value = get_number_input("Новый год: ")
    elif choice == 4:
        field = 'genre'
        new_value = get_input("Новый жанр: ")
    else:
        print("Неверный выбор")
        return
    
    if new_value is None or new_value == "":
        print("Ошибка: значение не может быть пустым")
        return
    
    try:
        updated = update_record('books', book_id, {field: new_value})
        print("Книга обновлена")
    except ValueError as e:
        print(f"Ошибка: {e}")

def remove_book():
    print("\n--- УДАЛЕНИЕ КНИГИ ---")
    
    book_id = get_number_input("Введите ID книги: ")
    if book_id is None:
        return
    
    try:
        deleted = delete_record('books', book_id)
        print(f"Книга '{deleted['title']}' удалена")
    except ValueError as e:
        print(f"Ошибка: {e}")

def create_new_table():
    print("\n--- СОЗДАНИЕ НОВОЙ ТАБЛИЦЫ ---")
    
    table_name = get_input("Введите имя таблицы: ")
    if not table_name:
        print("Ошибка: имя таблицы не может быть пустым")
        return
    
    try:
        create_table(table_name)
        print(f"Таблица '{table_name}' создана")
    except ValueError as e:
        print(f"Ошибка: {e}")

def show_all_tables():
    print("\n--- ТАБЛИЦЫ В БАЗЕ ДАННЫХ ---")
    tables = get_all_tables()
    for table in tables:
        print(f"- {table}")

def main_loop():
    while True:
        print_menu()
        choice = get_number_input("Выберите действие: ")
        
        if choice == 1:
            show_all_books()
        elif choice == 2:
            find_book()
        elif choice == 3:
            add_book()
        elif choice == 4:
            edit_book()
        elif choice == 5:
            remove_book()
        elif choice == 6:
            create_new_table()
        elif choice == 7:
            show_all_tables()
        elif choice == 0:
            print("До свидания!")
            break
        else:
            print("Неверный выбор, попробуйте снова")