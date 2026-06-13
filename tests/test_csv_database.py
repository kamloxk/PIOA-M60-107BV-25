import tempfile
import unittest
import shutil
from pathlib import Path
import csv
import json

from src.db.backend.csv_db import CsvDatabase
from src.db.backend.errors import TableNotFoundError, DuplicateTableError, InvalidStorageDataError


class TestCsvDatabase(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.db = CsvDatabase(self.test_dir)

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

    def test_select_with_filter(self):
        self.db.create_table('books', ('title', 'author', 'year'))
        self.db.insert_record('books', {'title': 'Book1', 'author': 'Author1', 'year': 2020})
        self.db.insert_record('books', {'title': 'Book2', 'author': 'Author2', 'year': 2021})
        records = self.db.select_records('books', author='Author2')
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]['title'], 'Book2')

    def test_update_record(self):
        self.db.create_table('books', ('title', 'author'))
        self.db.insert_record('books', {'title': 'Old', 'author': 'Author'})
        self.db.update_record('books', 1, {'title': 'New'})
        records = self.db.select_records('books')
        self.assertEqual(records[0]['title'], 'New')

    def test_delete_record(self):
        self.db.create_table('books', ('title', 'author'))
        self.db.insert_record('books', {'title': 'ToDelete', 'author': 'Author'})
        self.db.delete_record('books', 1)
        records = self.db.select_records('books')
        self.assertEqual(len(records), 0)

    def test_data_persists(self):
        self.db.create_table('books', ('title', 'author'))
        self.db.insert_record('books', {'title': 'Persistent', 'author': 'Author'})

        db2 = CsvDatabase(self.test_dir)
        records = db2.select_records('books')
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]['title'], 'Persistent')

    def test_list_tables(self):
        self.db.create_table('books', ('title',))
        self.db.create_table('authors', ('name',))
        tables = self.db.list_tables()
        self.assertIn('books', tables)
        self.assertIn('authors', tables)

    def test_select_from_missing_table(self):
        with self.assertRaises(TableNotFoundError):
            self.db.select_records('nonexistent')

    def test_create_and_use_index(self):
        self.db.create_table('books', ('title', 'author'))
        self.db.insert_record('books', {'title': 'Book1', 'author': 'Author1'})
        self.db.insert_record('books', {'title': 'Book2', 'author': 'Author2'})
        self.db.create_index('books', 'author')

        records = self.db.select_records('books', author='Author1')
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]['title'], 'Book1')


class TestCsvDatabaseStructure(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.db = CsvDatabase(self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_csv_and_schema_files_created(self):
        self.db.create_table('books', ('title', 'author'))
        self.db.insert_record('books', {'title': 'Test', 'author': 'Author'})

        csv_path = Path(self.test_dir) / 'books.csv'
        schema_path = Path(self.test_dir) / 'books_schema.json'

        self.assertTrue(csv_path.exists())
        self.assertTrue(schema_path.exists())

    def test_invalid_schema_file(self):
        schema_path = Path(self.test_dir) / 'invalid_schema.json'
        schema_path.write_text('not valid json', encoding='utf-8')
        csv_path = Path(self.test_dir) / 'invalid.csv'
        csv_path.write_text('id,title\n', encoding='utf-8')

        with self.assertRaises(InvalidStorageDataError):
            self.db.select_records('invalid')

if __name__ == '__main__':
    unittest.main()