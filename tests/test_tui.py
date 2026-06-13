import unittest
from unittest.mock import patch
from src.db.tui import LibraryApp, Menu, create_database
from src.db.backend.memory import MemoryDatabase
from src.db.backend.file import FileDatabase
from src.db.backend.csv_db import CsvDatabase


class TestMenu(unittest.TestCase):
    def test_menu_display(self):
        menu = Menu("Test", {"1": "Option 1", "2": "Option 2"})
        with patch('builtins.print') as mock_print:
            menu.display()
            calls = [str(c) for c in mock_print.call_args_list]
            self.assertTrue(any("Test" in c for c in calls))

    @patch('builtins.input', return_value="1")
    def test_menu_get_choice(self, mock_input):
        menu = Menu("Test", {"1": "Option 1"})
        choice = menu.get_choice()
        self.assertEqual(choice, "1")

    @patch('builtins.input', side_effect=EOFError)
    def test_menu_get_choice_eof(self, mock_input):
        menu = Menu("Test", {"1": "Option 1"})
        choice = menu.get_choice()
        self.assertEqual(choice, "0")


class TestLibraryApp(unittest.TestCase):
    def setUp(self):
        self.app = LibraryApp(database=MemoryDatabase())

    @patch('builtins.print')
    def test_print_books_empty(self, mock_print):
        self.app.print_books([])
        mock_print.assert_any_call("Книги не найдены")

    @patch('builtins.print')
    def test_print_books_with_data(self, mock_print):
        books = [{'id': 1, 'title': 'Test', 'author': 'Author', 'year': 2024, 'genre': 'Fiction'}]
        self.app.print_books(books)
        mock_print.assert_any_call("ID: 1")
        mock_print.assert_any_call("Название: Test")
        mock_print.assert_any_call("Автор: Author")
        mock_print.assert_any_call("Год: 2024")
        mock_print.assert_any_call("Жанр: Fiction")

    @patch('builtins.input', side_effect=["Test Book", "Test Author", "2024", "Fiction"])
    @patch('builtins.print')
    def test_add_book_success(self, mock_print, mock_input):
        self.app.add_book()
        mock_print.assert_any_call("Книга добавлена с ID: 1")

    @patch('builtins.input', side_effect=["", "Author", "2024", "Fiction"])
    @patch('builtins.print')
    def test_add_book_empty_title(self, mock_print, mock_input):
        self.app.add_book()
        mock_print.assert_any_call("Ошибка: название обязательно")

    @patch('builtins.input', side_effect=["Title", "", "2024", "Fiction"])
    @patch('builtins.print')
    def test_add_book_empty_author(self, mock_print, mock_input):
        self.app.add_book()
        mock_print.assert_any_call("Ошибка: автор обязателен")

    @patch('builtins.input', side_effect=["Title", "Author", "abc", "123", "Genre"])
    @patch('builtins.print')
    def test_add_book_invalid_year(self, mock_print, mock_input):
        self.app.add_book()
        mock_print.assert_any_call("Ошибка: введите число")

    @patch('builtins.input', side_effect=["Title", "Author", "2024", ""])
    @patch('builtins.print')
    def test_add_book_empty_genre(self, mock_print, mock_input):
        self.app.add_book()
        mock_print.assert_any_call("Ошибка: жанр обязателен")

    @patch('builtins.input', side_effect=EOFError)
    def test_get_input_eof(self, mock_input):
        result = self.app.get_input("Prompt: ")
        self.assertEqual(result, "")

    @patch('builtins.input', return_value="1")
    def test_get_input(self, mock_input):
        result = self.app.get_input("Prompt: ")
        self.assertEqual(result, "1")

    @patch('builtins.input', side_effect=["123"])
    def test_get_number_valid(self, mock_input):
        result = self.app.get_number("Prompt: ")
        self.assertEqual(result, 123)

    @patch('builtins.input', side_effect=["abc", "456"])
    @patch('builtins.print')
    def test_get_number_invalid_then_valid(self, mock_print, mock_input):
        result = self.app.get_number("Prompt: ")
        self.assertEqual(result, 456)
        mock_print.assert_any_call("Ошибка: введите число")

    @patch('builtins.input', side_effect=EOFError)
    def test_get_number_eof(self, mock_input):
        result = self.app.get_number("Prompt: ")
        self.assertIsNone(result)

    @patch('builtins.print')
    def test_show_all_books(self, mock_print):
        self.app.db.insert_record('books', {'title': 'Test', 'author': 'Author', 'year': 2024, 'genre': 'Fiction'})
        self.app.show_all_books()
        calls = [str(c) for c in mock_print.call_args_list]
        self.assertTrue(any("Test" in c for c in calls))

    @patch('builtins.input', side_effect=["1", "Test"])
    @patch('builtins.print')
    def test_find_book_by_title(self, mock_print, mock_input):
        self.app.db.insert_record('books', {'title': 'Test', 'author': 'Author', 'year': 2024, 'genre': 'Fiction'})
        self.app.find_book()
        mock_print.assert_any_call("ID: 1")

    @patch('builtins.input', side_effect=["2", "Author"])
    @patch('builtins.print')
    def test_find_book_by_author(self, mock_print, mock_input):
        self.app.db.insert_record('books', {'title': 'Test', 'author': 'Author', 'year': 2024, 'genre': 'Fiction'})
        self.app.find_book()
        mock_print.assert_any_call("ID: 1")

    @patch('builtins.input', side_effect=["3", "2024"])
    @patch('builtins.print')
    def test_find_book_by_year(self, mock_print, mock_input):
        self.app.db.insert_record('books', {'title': 'Test', 'author': 'Author', 'year': 2024, 'genre': 'Fiction'})
        self.app.find_book()
        mock_print.assert_any_call("ID: 1")

    @patch('builtins.input', side_effect=["4", "Fiction"])
    @patch('builtins.print')
    def test_find_book_by_genre(self, mock_print, mock_input):
        self.app.db.insert_record('books', {'title': 'Test', 'author': 'Author', 'year': 2024, 'genre': 'Fiction'})
        self.app.find_book()
        mock_print.assert_any_call("ID: 1")

    @patch('builtins.input', side_effect=["5"])
    @patch('builtins.print')
    def test_find_book_invalid_choice(self, mock_print, mock_input):
        self.app.find_book()
        mock_print.assert_any_call("Неверный выбор")

    @patch('builtins.input', side_effect=["1", ""])
    @patch('builtins.print')
    def test_find_book_empty_value(self, mock_print, mock_input):
        self.app.db.insert_record('books', {'title': 'Test', 'author': 'Author', 'year': 2024, 'genre': 'Fiction'})
        self.app.find_book()

    @patch('builtins.input', side_effect=["1", "1", "New Title"])
    @patch('builtins.print')
    def test_edit_book_title(self, mock_print, mock_input):
        self.app.db.insert_record('books', {'title': 'Old', 'author': 'Author', 'year': 2024, 'genre': 'Fiction'})
        self.app.edit_book()
        mock_print.assert_any_call("Книга обновлена")
        updated = self.app.db.select_records('books')[0]
        self.assertEqual(updated['title'], 'New Title')

    @patch('builtins.input', side_effect=["1", "2", "New Author"])
    @patch('builtins.print')
    def test_edit_book_author(self, mock_print, mock_input):
        self.app.db.insert_record('books', {'title': 'Test', 'author': 'Old', 'year': 2024, 'genre': 'Fiction'})
        self.app.edit_book()
        mock_print.assert_any_call("Книга обновлена")
        updated = self.app.db.select_records('books')[0]
        self.assertEqual(updated['author'], 'New Author')

    @patch('builtins.input', side_effect=["1", "3", "2025"])
    @patch('builtins.print')
    def test_edit_book_year(self, mock_print, mock_input):
        self.app.db.insert_record('books', {'title': 'Test', 'author': 'Author', 'year': 2024, 'genre': 'Fiction'})
        self.app.edit_book()
        mock_print.assert_any_call("Книга обновлена")
        updated = self.app.db.select_records('books')[0]
        self.assertEqual(updated['year'], 2025)

    @patch('builtins.input', side_effect=["1", "4", "New Genre"])
    @patch('builtins.print')
    def test_edit_book_genre(self, mock_print, mock_input):
        self.app.db.insert_record('books', {'title': 'Test', 'author': 'Author', 'year': 2024, 'genre': 'Old'})
        self.app.edit_book()
        mock_print.assert_any_call("Книга обновлена")
        updated = self.app.db.select_records('books')[0]
        self.assertEqual(updated['genre'], 'New Genre')

    @patch('builtins.input', side_effect=["1", "5"])
    @patch('builtins.print')
    def test_edit_book_invalid_choice(self, mock_print, mock_input):
        self.app.db.insert_record('books', {'title': 'Test', 'author': 'Author', 'year': 2024, 'genre': 'Fiction'})
        self.app.edit_book()
        mock_print.assert_any_call("Неверный выбор")

    @patch('builtins.input', side_effect=["1", "1", ""])
    @patch('builtins.print')
    def test_edit_book_empty_value(self, mock_print, mock_input):
        self.app.db.insert_record('books', {'title': 'Test', 'author': 'Author', 'year': 2024, 'genre': 'Fiction'})
        self.app.edit_book()
        mock_print.assert_any_call("Ошибка: значение не может быть пустым")

    @patch('builtins.input', side_effect=[None])
    @patch('builtins.print')
    def test_edit_book_no_id(self, mock_print, mock_input):
        with patch.object(self.app, 'get_number', return_value=None):
            self.app.edit_book()

    @patch('builtins.input', side_effect=["1"])
    @patch('builtins.print')
    def test_remove_book(self, mock_print, mock_input):
        self.app.db.insert_record('books', {'title': 'ToDelete', 'author': 'Author', 'year': 2024, 'genre': 'Fiction'})
        self.app.remove_book()
        mock_print.assert_any_call("Книга 'ToDelete' удалена")

    @patch('builtins.input', side_effect=["999"])
    @patch('builtins.print')
    def test_remove_book_not_found(self, mock_print, mock_input):
        self.app.db.insert_record('books', {'title': 'Test', 'author': 'Author', 'year': 2024, 'genre': 'Fiction'})
        self.app.remove_book()
        calls = [str(c) for c in mock_print.call_args_list]
        self.assertTrue(any("Ошибка" in c for c in calls))

    @patch('builtins.input', side_effect=[None])
    @patch('builtins.print')
    def test_remove_book_no_id(self, mock_print, mock_input):
        with patch.object(self.app, 'get_number', return_value=None):
            self.app.remove_book()

    @patch('builtins.input', side_effect=["1", "1"])
    @patch('builtins.print')
    def test_sort_books_asc(self, mock_print, mock_input):
        self.app.db.insert_record('books', {'title': 'Zebra', 'author': 'A', 'year': 2024, 'genre': 'Fiction'})
        self.app.db.insert_record('books', {'title': 'Apple', 'author': 'B', 'year': 2023, 'genre': 'Fiction'})
        self.app.sort_books()
        calls = str(mock_print.call_args_list)
        self.assertIn("Apple", calls)

    @patch('builtins.input', side_effect=["1", "2"])
    @patch('builtins.print')
    def test_sort_books_desc(self, mock_print, mock_input):
        self.app.db.insert_record('books', {'title': 'Apple', 'author': 'A', 'year': 2024, 'genre': 'Fiction'})
        self.app.db.insert_record('books', {'title': 'Zebra', 'author': 'B', 'year': 2023, 'genre': 'Fiction'})
        self.app.sort_books()
        calls = str(mock_print.call_args_list)
        self.assertIn("Zebra", calls)

    @patch('builtins.input', side_effect=["2", "1"])
    @patch('builtins.print')
    def test_sort_books_by_author(self, mock_print, mock_input):
        self.app.db.insert_record('books', {'title': 'A', 'author': 'Zoe', 'year': 2024, 'genre': 'Fiction'})
        self.app.db.insert_record('books', {'title': 'B', 'author': 'Adam', 'year': 2023, 'genre': 'Fiction'})
        self.app.sort_books()
        calls = str(mock_print.call_args_list)
        self.assertIn("Adam", calls)

    @patch('builtins.input', side_effect=["3", "1"])
    @patch('builtins.print')
    def test_sort_books_by_year(self, mock_print, mock_input):
        self.app.db.insert_record('books', {'title': 'A', 'author': 'A', 'year': 2024, 'genre': 'Fiction'})
        self.app.db.insert_record('books', {'title': 'B', 'author': 'B', 'year': 2020, 'genre': 'Fiction'})
        self.app.sort_books()

    @patch('builtins.input', side_effect=["4", "2"])
    @patch('builtins.print')
    def test_sort_books_by_genre_desc(self, mock_print, mock_input):
        self.app.db.insert_record('books', {'title': 'A', 'author': 'A', 'year': 2024, 'genre': 'Fiction'})
        self.app.db.insert_record('books', {'title': 'B', 'author': 'B', 'year': 2023, 'genre': 'Science'})
        self.app.sort_books()

    @patch('builtins.input', side_effect=["5", "1"])
    @patch('builtins.print')
    def test_sort_books_invalid_field(self, mock_print, mock_input):
        self.app.db.insert_record('books', {'title': 'Test', 'author': 'Author', 'year': 2024, 'genre': 'Fiction'})
        self.app.sort_books()
        mock_print.assert_any_call("Неверный выбор")

    @patch('builtins.input', return_value="new_table")
    @patch('builtins.print')
    def test_create_table_ui(self, mock_print, mock_input):
        self.app.create_table_ui()
        mock_print.assert_any_call("Таблица 'new_table' создана")

    @patch('builtins.input', return_value="")
    @patch('builtins.print')
    def test_create_table_ui_empty_name(self, mock_print, mock_input):
        self.app.create_table_ui()
        mock_print.assert_any_call("Ошибка: имя не может быть пустым")

    @patch('builtins.input', return_value="books")
    @patch('builtins.print')
    def test_create_table_ui_duplicate(self, mock_print, mock_input):
        self.app.create_table_ui()
        calls = [str(c) for c in mock_print.call_args_list]
        self.assertTrue(any("Ошибка" in c for c in calls))

    @patch('builtins.print')
    def test_show_tables(self, mock_print):
        self.app.db.create_table('authors', ('name',))
        self.app.show_tables()
        mock_print.assert_any_call("- authors")

    @patch('builtins.input', side_effect=["1"])
    @patch('builtins.print')
    def test_create_index_ui(self, mock_print, mock_input):
        self.app.db.insert_record('books', {'title': 'Test', 'author': 'Author', 'year': 2024, 'genre': 'Fiction'})
        self.app.create_index_ui()
        mock_print.assert_any_call("Индекс по полю 'title' создан")

    @patch('builtins.input', side_effect=["2"])
    @patch('builtins.print')
    def test_create_index_ui_author(self, mock_print, mock_input):
        self.app.db.insert_record('books', {'title': 'Test', 'author': 'Author', 'year': 2024, 'genre': 'Fiction'})
        self.app.create_index_ui()
        mock_print.assert_any_call("Индекс по полю 'author' создан")

    @patch('builtins.input', side_effect=["3"])
    @patch('builtins.print')
    def test_create_index_ui_year(self, mock_print, mock_input):
        self.app.db.insert_record('books', {'title': 'Test', 'author': 'Author', 'year': 2024, 'genre': 'Fiction'})
        self.app.create_index_ui()
        mock_print.assert_any_call("Индекс по полю 'year' создан")

    @patch('builtins.input', side_effect=["4"])
    @patch('builtins.print')
    def test_create_index_ui_genre(self, mock_print, mock_input):
        self.app.db.insert_record('books', {'title': 'Test', 'author': 'Author', 'year': 2024, 'genre': 'Fiction'})
        self.app.create_index_ui()
        mock_print.assert_any_call("Индекс по полю 'genre' создан")

    @patch('builtins.input', side_effect=["5"])
    @patch('builtins.print')
    def test_create_index_ui_invalid(self, mock_print, mock_input):
        self.app.create_index_ui()
        mock_print.assert_any_call("Неверный выбор")


class TestCreateDatabase(unittest.TestCase):
    @patch('builtins.input', return_value="1")
    def test_create_memory_database(self, mock_input):
        db = create_database()
        self.assertIsInstance(db, MemoryDatabase)

    @patch('builtins.input', return_value="2")
    def test_create_file_database(self, mock_input):
        db = create_database()
        self.assertIsInstance(db, FileDatabase)

    @patch('builtins.input', return_value="3")
    def test_create_csv_database(self, mock_input):
        db = create_database()
        self.assertIsInstance(db, CsvDatabase)


if __name__ == '__main__':
    unittest.main()