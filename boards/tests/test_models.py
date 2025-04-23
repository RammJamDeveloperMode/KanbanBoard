import unittest
from boards.dynamodb import DynamoDBAdapter

class TestModels(unittest.TestCase):
    def setUp(self):
        self.db = DynamoDBAdapter()
        self.board_id = self.db.create_board("Test Board")
        self.column_id = self.db.create_column(self.board_id, "Test Column", 1)
        self.card_id = self.db.create_card(self.column_id, "Test Card", "Test Description", 1)

    def test_board_creation(self):
        """Test that a board can be created"""
        boards = self.db.get_boards()
        board = next((b for b in boards if b['id'] == self.board_id), None)
        self.assertIsNotNone(board)
        self.assertEqual(board['name'], "Test Board")

    def test_column_creation(self):
        """Test that a column can be created"""
        columns = self.db.get_columns(self.board_id)
        column = next((c for c in columns if c['id'] == self.column_id), None)
        self.assertIsNotNone(column)
        self.assertEqual(column['name'], "Test Column")
        self.assertEqual(column['board_id'], self.board_id)
        self.assertEqual(column['order'], 1)

    def test_card_creation(self):
        """Test that a card can be created"""
        cards = self.db.get_cards(self.column_id)
        card = next((c for c in cards if c['id'] == self.card_id), None)
        self.assertIsNotNone(card)
        self.assertEqual(card['title'], "Test Card")
        self.assertEqual(card['description'], "Test Description")
        self.assertEqual(card['column_id'], self.column_id)
        self.assertEqual(card['order'], 1)

    def test_column_deletion_cascade(self):
        """Test that cards are deleted when a column is deleted"""
        self.db.delete_column(self.column_id)
        cards = self.db.get_cards(self.column_id)
        self.assertEqual(len(cards), 0)

    def test_board_deletion_cascade(self):
        """Test that columns and cards are deleted when a board is deleted"""
        self.db.delete_board(self.board_id)
        columns = self.db.get_columns(self.board_id)
        self.assertEqual(len(columns), 0)
        cards = self.db.get_cards(self.column_id)
        self.assertEqual(len(cards), 0)

    def tearDown(self):
        """Clean up after each test"""
        try:
            self.db.delete_board(self.board_id)
        except Exception:
            pass  # El board ya pudo haber sido eliminado por un test 