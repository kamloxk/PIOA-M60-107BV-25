import unittest
from src.db.backend.table import Table
from src.db.backend.errors import MissingColumnError, UnknownColumnError, RecordNotFoundError


class TestTable(unittest.TestCase):
    def setUp(self):
        self.table = Table(('title', 'author', 'year', 'genre'))

    def test_insert_record(self):
        record_id = self.table.insert_record({'title': 'Test', 'author': 'Author', 'year': 2024, 'genre': 'Fiction'})
        self.assertEqual(record_id, 1)
        self.assertEqual(len(self.table.records), 1)

    def test_insert_record_with_id(self):
        self.table.insert_record({'id': 5, 'title': 'Test', 'author': 'Author', 'year': 2024, 'genre': 'Fiction'})
        self.assertEqual(self.table.records[0]['id'], 5)    

    def test_insert_record_missing_column(self):
        with self.assertRaises(MissingColumnError):
            self.table.insert_record({'title': 'Test'})

    def test_insert_record_unknown_column(self):
        with self.assertRaises(UnknownColumnError):
            self.table.insert_record({'title': 'Test', 'author': 'Author', 'year': 2024, 'genre': 'Fiction', 'extra': 'data'})

    def test_select_records_no_filters(self):
        self.table.insert_record({'title': 'Test1', 'author': 'Author1', 'year': 2024, 'genre': 'Fiction'})
        self.table.insert_record({'title': 'Test2', 'author': 'Author2', 'year': 2023, 'genre': 'Science'})
        records = self.table.select_records()
        self.assertEqual(len(records), 2)

    def test_select_records_with_filter(self):
        self.table.insert_record({'title': 'Test1', 'author': 'Author1', 'year': 2024, 'genre': 'Fiction'})
        self.table.insert_record({'title': 'Test2', 'author': 'Author2', 'year': 2023, 'genre': 'Science'})
        records = self.table.select_records(author='Author1')
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]['title'], 'Test1')

    def test_select_records_unknown_filter(self):
        with self.assertRaises(UnknownColumnError):
            self.table.select_records(unknown_field='value')

    def test_select_records_with_index(self):
        self.table.insert_record({'title': 'Test1', 'author': 'Author1', 'year': 2024, 'genre': 'Fiction'})
        self.table.insert_record({'title': 'Test2', 'author': 'Author2', 'year': 2023, 'genre': 'Science'})
        self.table.create_index('author')
        records = self.table.select_records(author='Author1')
        self.assertEqual(len(records), 1)

    def test_select_records_with_index_no_match(self):
        self.table.insert_record({'title': 'Test1', 'author': 'Author1', 'year': 2024, 'genre': 'Fiction'})
        self.table.create_index('author')
        records = self.table.select_records(author='Unknown')
        self.assertEqual(len(records), 0)

    def test_update_record(self):
        self.table.insert_record({'title': 'Old', 'author': 'Author', 'year': 2024, 'genre': 'Fiction'})
        updated = self.table.update_record(1, {'title': 'New'})
        self.assertEqual(updated['title'], 'New')

    def test_update_record_not_found(self):
        with self.assertRaises(RecordNotFoundError):
            self.table.update_record(999, {'title': 'Test'})

    def test_update_record_unknown_column(self):
        self.table.insert_record({'title': 'Test', 'author': 'Author', 'year': 2024, 'genre': 'Fiction'})
        with self.assertRaises(UnknownColumnError):
            self.table.update_record(1, {'extra': 'data'})

    def test_update_record_with_index(self):
        self.table.insert_record({'title': 'Test', 'author': 'Old', 'year': 2024, 'genre': 'Fiction'})
        self.table.create_index('author')
        self.table.update_record(1, {'author': 'New'})
        records = self.table.select_records(author='New')
        self.assertEqual(len(records), 1)
        records = self.table.select_records(author='Old')
        self.assertEqual(len(records), 0)

    def test_delete_record(self):
        self.table.insert_record({'title': 'Test', 'author': 'Author', 'year': 2024, 'genre': 'Fiction'})
        deleted = self.table.delete_record(1)
        self.assertEqual(deleted['title'], 'Test')
        self.assertEqual(len(self.table.records), 0)

    def test_delete_record_not_found(self):
        with self.assertRaises(RecordNotFoundError):
            self.table.delete_record(999)

    def test_delete_record_with_index(self):
        self.table.insert_record({'title': 'Test', 'author': 'Author', 'year': 2024, 'genre': 'Fiction'})
        self.table.create_index('author')
        self.table.delete_record(1)
        records = self.table.select_records(author='Author')
        self.assertEqual(len(records), 0)

    def test_create_index(self):
        self.table.insert_record({'title': 'Test1', 'author': 'Author1', 'year': 2024, 'genre': 'Fiction'})
        self.table.insert_record({'title': 'Test2', 'author': 'Author2', 'year': 2023, 'genre': 'Science'})
        self.table.create_index('author')
        self.assertIn('author', self.table.indexes)

    def test_create_index_unknown_column(self):
        with self.assertRaises(UnknownColumnError):
            self.table.create_index('unknown')

    def test_count(self):
        self.assertEqual(self.table.count(), 0)
        self.table.insert_record({'title': 'Test', 'author': 'Author', 'year': 2024, 'genre': 'Fiction'})
        self.assertEqual(self.table.count(), 1)

    def test_init_with_records(self):
        records = [{'title': 'Test', 'author': 'Author', 'year': 2024, 'genre': 'Fiction'}]
        table = Table(('title', 'author', 'year', 'genre'), records)
        self.assertEqual(len(table.records), 1)


if __name__ == '__main__':
    unittest.main()