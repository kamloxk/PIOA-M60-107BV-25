import unittest
from src.db.backend.memory import Database, Table, Record
from src.db.backend.errors import (
    TableNotFoundError,
    RecordNotFoundError,
    DuplicateTableError
)


class TestRecord(unittest.TestCase):
    def test_create_record(self):
        r = Record(1, {'title': 'Test', 'year': 2024})
        self.assertEqual(r.id, 1)
        self.assertEqual(r.data['title'], 'Test')
    
    def test_to_dict(self):
        r = Record(2, {'author': 'Author'})
        result = r.to_dict()
        self.assertEqual(result['id'], 2)
        self.assertEqual(result['author'], 'Author')
    
    def test_update(self):
        r = Record(3, {'title': 'Old'})
        r.update({'title': 'New', 'year': 2025})
        self.assertEqual(r.data['title'], 'New')
        self.assertEqual(r.data['year'], 2025)


class TestTable(unittest.TestCase):
    def setUp(self):
        self.table = Table('books')
    
    def test_create(self):
        record = self.table.create({'title': 'Book1'})
        self.assertEqual(record.id, 1)
        self.assertEqual(self.table.count(), 1)
    
    def test_select_all(self):
        self.table.create({'title': 'Book1'})
        self.table.create({'title': 'Book2'})
        results = self.table.select()
        self.assertEqual(len(results), 2)
    
    def test_select_with_filter(self):
        self.table.create({'title': 'Book1', 'year': 2020})
        self.table.create({'title': 'Book2', 'year': 2021})
        results = self.table.select({'year': 2021})
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'Book2')
    
    def test_update_existing(self):
        record = self.table.create({'title': 'Book1'})
        updated = self.table.update(record.id, {'title': 'Updated'})
        self.assertEqual(updated.data['title'], 'Updated')
    
    def test_update_not_found(self):
        with self.assertRaises(RecordNotFoundError):
            self.table.update(999, {'title': 'Test'})
    
    def test_delete_existing(self):
        record = self.table.create({'title': 'Book1'})
        deleted = self.table.delete(record.id)
        self.assertEqual(deleted.id, record.id)
        self.assertEqual(self.table.count(), 0)
    
    def test_delete_not_found(self):
        with self.assertRaises(RecordNotFoundError):
            self.table.delete(999)
    
    def test_sort_asc(self):
        self.table.create({'title': 'C', 'year': 2022})
        self.table.create({'title': 'A', 'year': 2020})
        self.table.create({'title': 'B', 'year': 2021})
        results = self.table.select(sort_by='title', sort_order='asc')
        self.assertEqual(results[0]['title'], 'A')
        self.assertEqual(results[1]['title'], 'B')
        self.assertEqual(results[2]['title'], 'C')
    
    def test_sort_desc(self):
        self.table.create({'title': 'A', 'year': 2020})
        self.table.create({'title': 'C', 'year': 2022})
        self.table.create({'title': 'B', 'year': 2021})
        results = self.table.select(sort_by='title', sort_order='desc')
        self.assertEqual(results[0]['title'], 'C')
        self.assertEqual(results[1]['title'], 'B')
        self.assertEqual(results[2]['title'], 'A')
    
    def test_sort_by_year(self):
        self.table.create({'title': 'Book1', 'year': 2022})
        self.table.create({'title': 'Book2', 'year': 2020})
        results = self.table.select(sort_by='year', sort_order='asc')
        self.assertEqual(results[0]['year'], 2020)
        self.assertEqual(results[1]['year'], 2022)


class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.db = Database()
    
    def test_create_table(self):
        table = self.db.create_table('books')
        self.assertEqual(table.name, 'books')
    
    def test_create_duplicate_table(self):
        self.db.create_table('books')
        with self.assertRaises(DuplicateTableError):
            self.db.create_table('books')
    
    def test_get_table_not_found(self):
        with self.assertRaises(TableNotFoundError):
            self.db.get_table('nonexistent')
    
    def test_list_tables(self):
        self.db.create_table('books')
        self.db.create_table('authors')
        tables = self.db.list_tables()
        self.assertIn('books', tables)
        self.assertIn('authors', tables)
    
    def test_crud_operations(self):
        self.db.create_table('books')
        record = self.db.create_record('books', {'title': 'Test'})
        self.assertIsNotNone(record)
        
        results = self.db.select_records('books')
        self.assertEqual(len(results), 1)
        
        self.db.update_record('books', record.id, {'title': 'Updated'})
        updated = self.db.select_records('books')[0]
        self.assertEqual(updated['title'], 'Updated')
        
        self.db.delete_record('books', record.id)
        results = self.db.select_records('books')
        self.assertEqual(len(results), 0)


if __name__ == '__main__':
    unittest.main()