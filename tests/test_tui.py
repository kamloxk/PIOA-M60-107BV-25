import unittest
from unittest.mock import patch
from src.db.tui import LibraryApp, Menu
from src.db.backend.memory import MemoryDatabase


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

    @patch('builtins.input', side_effect=["1", "1", "New Title"])
    @patch('builtins.print')
    def test_edit_book_title(self, mock_print, mock_input):
        self.app.db.insert_record('books', {'title': 'Old', 'author': 'Author', 'year': 2024, 'genre': 'Fiction'})
        self.app.edit_book()
        mock_print.assert_any_call("Книга обновлена")
        updated = self.app.db.select_records('books')[0]
        self.assertEqual(updated['title'], 'New Title')

    @patch('builtins.input', side_effect=["1"])
    @patch('builtins.print')
    def test_remove_book(self, mock_print, mock_input):
        self.app.db.insert_record('books', {'title': 'ToDelete', 'author': 'Author', 'year': 2024, 'genre': 'Fiction'})
        self.app.remove_book()
        mock_print.assert_any_call("Книга 'ToDelete' удалена")

    @patch('builtins.input', side_effect=["1", "1"])
    @patch('builtins.print')
    def test_sort_books_asc(self, mock_print, mock_input):
        self.app.db.insert_record('books', {'title': 'Zebra', 'author': 'A', 'year': 2024, 'genre': 'Fiction'})
        self.app.db.insert_record('books', {'title': 'Apple', 'author': 'B', 'year': 2023, 'genre': 'Fiction'})
        self.app.sort_books()
        calls = str(mock_print.call_args_list)
        self.assertIn("Apple", calls)

    @patch('builtins.input', return_value="new_table")
    @patch('builtins.print')
    def test_create_table_ui(self, mock_print, mock_input):
        self.app.create_table_ui()
        mock_print.assert_any_call("Таблица 'new_table' создана")

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


if __name__ == '__main__':
    unittest.main()