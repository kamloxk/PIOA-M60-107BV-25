import unittest
from src.db.backend.memory import MemoryDatabase
from src.db.backend.errors import TableNotFoundError, RecordNotFoundError, DuplicateTableError


class TestMemoryDatabase(unittest.TestCase):
    def setUp(self):
        self.db = MemoryDatabase()

    def test_create_table(self):
        self.db.create_table('books', ('title', 'author'))
        self.assertIn('books', self.db.list_tables())

    def test_create_duplicate_table(self):
        self.db.create_table('books', ('title',))
        with self.assertRaises(DuplicateTableError):
            self.db.create_table('books', ('title',))

    def test_insert_record(self):
        self.db.create_table('books', ('title', 'author'))
        record_id = self.db.insert_record('books', {'title': 'Test', 'author': 'Author'})
        self.assertEqual(record_id, 1)

    def test_insert_record_into_missing_table(self):
        with self.assertRaises(TableNotFoundError):
            self.db.insert_record('nonexistent', {'title': 'Test'})

    def test_select_records(self):
        self.db.create_table('books', ('title', 'author'))
        self.db.insert_record('books', {'title': 'Book1', 'author': 'Author1'})
        self.db.insert_record('books', {'title': 'Book2', 'author': 'Author2'})
        records = self.db.select_records('books')
        self.assertEqual(len(records), 2)

    def test_select_records_from_missing_table(self):
        with self.assertRaises(TableNotFoundError):
            self.db.select_records('nonexistent')

    def test_select_with_filter(self):
        self.db.create_table('books', ('title', 'author'))
        self.db.insert_record('books', {'title': 'Book1', 'author': 'Author1'})
        self.db.insert_record('books', {'title': 'Book2', 'author': 'Author2'})
        records = self.db.select_records('books', author='Author2')
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]['title'], 'Book2')

    def test_update_record(self):
        self.db.create_table('books', ('title', 'author'))
        self.db.insert_record('books', {'title': 'Old', 'author': 'Author'})
        self.db.update_record('books', 1, {'title': 'New'})
        records = self.db.select_records('books')
        self.assertEqual(records[0]['title'], 'New')

    def test_update_record_from_missing_table(self):
        with self.assertRaises(TableNotFoundError):
            self.db.update_record('nonexistent', 1, {'title': 'Test'})

    def test_update_nonexistent_record(self):
        self.db.create_table('books', ('title', 'author'))
        with self.assertRaises(RecordNotFoundError):
            self.db.update_record('books', 999, {'title': 'Test'})

    def test_delete_record(self):
        self.db.create_table('books', ('title', 'author'))
        self.db.insert_record('books', {'title': 'ToDelete', 'author': 'Author'})
        self.db.delete_record('books', 1)
        records = self.db.select_records('books')
        self.assertEqual(len(records), 0)

    def test_delete_record_from_missing_table(self):
        with self.assertRaises(TableNotFoundError):
            self.db.delete_record('nonexistent', 1)

    def test_delete_nonexistent_record(self):
        self.db.create_table('books', ('title', 'author'))
        with self.assertRaises(RecordNotFoundError):
            self.db.delete_record('books', 999)

    def test_create_index(self):
        self.db.create_table('books', ('title', 'author'))
        self.db.insert_record('books', {'title': 'Book1', 'author': 'Author1'})
        self.db.create_index('books', 'author')
        records = self.db.select_records('books', author='Author1')
        self.assertEqual(len(records), 1)

    def test_create_index_from_missing_table(self):
        with self.assertRaises(TableNotFoundError):
            self.db.create_index('nonexistent', 'author')

    def test_list_tables_empty(self):
        self.assertEqual(self.db.list_tables(), [])


if __name__ == '__main__':
    unittest.main()