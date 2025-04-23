import unittest
from graphene.test import Client
from kanban_backend.schema import schema
from boards.dynamodb import DynamoDBAdapter

class TestMutations(unittest.TestCase):
    def setUp(self):
        self.client = Client(schema)
        self.db = DynamoDBAdapter()
        self.board_id = self.db.create_board("Test Board")
        self.column_id = self.db.create_column(self.board_id, "Test Column", 1)
        self.card_id = self.db.create_card(self.column_id, "Test Card", "Test Description", 1)

    def test_create_board(self):
        """Test that a board can be created"""
        executed = self.client.execute('''
            mutation {
                createBoard(name: "New Board") {
                    board {
                        id
                        name
                    }
                }
            }
        ''')
        assert executed['data']['createBoard']['board']['name'] == "New Board"

    def test_create_column(self):
        """Test that a column can be created"""
        executed = self.client.execute('''
            mutation {
                createColumn(boardId: "%s", name: "New Column", order: 1) {
                    column {
                        id
                        name
                        order
                    }
                }
            }
        ''' % self.board_id)
        assert executed['data']['createColumn']['column']['name'] == "New Column"
        assert executed['data']['createColumn']['column']['order'] == 1

    def test_create_card(self):
        """Test that a card can be created"""
        executed = self.client.execute('''
            mutation {
                createCard(columnId: "%s", title: "New Card", description: "New Description", order: 1) {
                    card {
                        id
                        title
                        description
                        order
                    }
                }
            }
        ''' % self.column_id)
        assert executed['data']['createCard']['card']['title'] == "New Card"
        assert executed['data']['createCard']['card']['description'] == "New Description"
        assert executed['data']['createCard']['card']['order'] == 1

    def test_move_card(self):
        """Test that a card can be moved to a different column"""
        new_column_id = self.db.create_column(self.board_id, "New Column", 2)
        executed = self.client.execute('''
            mutation {
                moveCard(id: "%s", columnId: "%s", order: 1) {
                    success
                }
            }
        ''' % (self.card_id, new_column_id))
        assert executed['data']['moveCard']['success'] == True

    def test_move_column(self):
        """Test that a column can be moved to a different position"""
        executed = self.client.execute('''
            mutation {
                moveColumn(id: "%s", order: 2) {
                    success
                }
            }
        ''' % self.column_id)
        assert executed['data']['moveColumn']['success'] == True

    def tearDown(self):
        """Clean up after each test"""
        try:
            self.db.delete_board(self.board_id)
        except Exception:
            pass  # El board ya pudo haber sido eliminado por un test 