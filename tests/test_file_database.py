import tempfile
import unittest
import shutil
from pathlib import Path
import json

from src.db.backend.file import FileDatabase
from src.db.backend.errors import TableNotFoundError, DuplicateTableError, InvalidStorageDataError


class TestFileDatabase(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.db = FileDatabase(self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_create_table(self):
        self.db.create_table('books', ('title', 'author'))
        self.assertTrue(self.db._table_exists('books'))

    def test_create_duplicate_table(self):
        self.db.create_table('books', ('title',))
        with self.assertRaises(DuplicateTableError):
            self.db.create_table('books', ('title',))

    def test_insert_and_select(self):
        self.db.create_table('books', ('title', 'author', 'year'))
        self.db.insert_record('books', {'title': 'Test', 'author': 'Author', 'year': 2024})
        records = self.db.select_records('books')
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]['title'], 'Test')

    def test_insert_into_missing_table(self):
        with self.assertRaises(TableNotFoundError):
            self.db.insert_record('nonexistent', {'title': 'Test'})

    def test_select_with_filter(self):
        self.db.create_table('books', ('title', 'author', 'year'))
        self.db.insert_record('books', {'title': 'Book1', 'author': 'Author1', 'year': 2020})
        self.db.insert_record('books', {'title': 'Book2', 'author': 'Author2', 'year': 2021})
        records = self.db.select_records('books', author='Author2')
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]['title'], 'Book2')

    def test_select_from_missing_table(self):
        with self.assertRaises(TableNotFoundError):
            self.db.select_records('nonexistent')

    def test_update_record(self):
        self.db.create_table('books', ('title', 'author'))
        self.db.insert_record('books', {'title': 'Old', 'author': 'Author'})
        self.db.update_record('books', 1, {'title': 'New'})
        records = self.db.select_records('books')
        self.assertEqual(records[0]['title'], 'New')

    def test_update_record_from_missing_table(self):
        with self.assertRaises(TableNotFoundError):
            self.db.update_record('nonexistent', 1, {'title': 'Test'})

    def test_delete_record(self):
        self.db.create_table('books', ('title', 'author'))
        self.db.insert_record('books', {'title': 'ToDelete', 'author': 'Author'})
        self.db.delete_record('books', 1)
        records = self.db.select_records('books')
        self.assertEqual(len(records), 0)

    def test_delete_record_from_missing_table(self):
        with self.assertRaises(TableNotFoundError):
            self.db.delete_record('nonexistent', 1)

    def test_data_persists(self):
        self.db.create_table('books', ('title', 'author'))
        self.db.insert_record('books', {'title': 'Persistent', 'author': 'Author'})

        db2 = FileDatabase(self.test_dir)
        records = db2.select_records('books')
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]['title'], 'Persistent')

    def test_list_tables(self):
        self.db.create_table('books', ('title',))
        self.db.create_table('authors', ('name',))
        tables = self.db.list_tables()
        self.assertIn('books', tables)
        self.assertIn('authors', tables)

    def test_list_tables_empty_directory(self):
        empty_dir = tempfile.mkdtemp()
        db = FileDatabase(empty_dir)
        self.assertEqual(db.list_tables(), [])
        shutil.rmtree(empty_dir)

    def test_create_and_use_index(self):
        self.db.create_table('books', ('title', 'author'))
        self.db.insert_record('books', {'title': 'Book1', 'author': 'Author1'})
        self.db.insert_record('books', {'title': 'Book2', 'author': 'Author2'})
        self.db.create_index('books', 'author')

        records = self.db.select_records('books', author='Author1')
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]['title'], 'Book1')

    def test_create_index_from_missing_table(self):
        with self.assertRaises(TableNotFoundError):
            self.db.create_index('nonexistent', 'author')

    def test_index_updates_on_insert(self):
        self.db.create_table('books', ('title', 'author'))
        self.db.create_index('books', 'author')
        self.db.insert_record('books', {'title': 'Book1', 'author': 'Author1'})

        records = self.db.select_records('books', author='Author1')
        self.assertEqual(len(records), 1)

    def test_index_updates_on_delete(self):
        self.db.create_table('books', ('title', 'author'))
        self.db.insert_record('books', {'title': 'Book1', 'author': 'Author1'})
        self.db.create_index('books', 'author')
        self.db.delete_record('books', 1)

        records = self.db.select_records('books', author='Author1')
        self.assertEqual(len(records), 0)


class TestFileDatabaseJSONStructure(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.db = FileDatabase(self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_json_file_structure(self):
        self.db.create_table('books', ('title', 'author', 'year', 'genre'))
        self.db.insert_record('books', {'title': 'Test', 'author': 'Author', 'year': 2024, 'genre': 'Fiction'})

        table_path = Path(self.test_dir) / 'books.json'
        with table_path.open('r', encoding='utf-8') as f:
            data = json.load(f)

        self.assertIn('columns', data)
        self.assertIn('records', data)
        self.assertIn('next_id', data)
        self.assertEqual(data['columns'], ['title', 'author', 'year', 'genre'])
        self.assertEqual(len(data['records']), 1)

    def test_invalid_json_file(self):
        table_path = Path(self.test_dir) / 'invalid.json'
        table_path.write_text('not valid json', encoding='utf-8')

        with self.assertRaises(InvalidStorageDataError):
            self.db.select_records('invalid')

    def test_missing_columns_in_json(self):
        table_path = Path(self.test_dir) / 'bad.json'
        with table_path.open('w', encoding='utf-8') as f:
            json.dump({'wrong_key': 'value'}, f)

        with self.assertRaises(InvalidStorageDataError):
            self.db.select_records('bad')


if __name__ == '__main__':
    unittest.main()