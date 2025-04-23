import graphene
from graphene_django import DjangoObjectType
from kanban_backend.boards.dynamodb import DynamoDBAdapter
import logging

logger = logging.getLogger(__name__)

db = DynamoDBAdapter()

class BoardType(graphene.ObjectType):
    id = graphene.ID()
    type = graphene.String()
    name = graphene.String()
    created_at = graphene.String()
    updated_at = graphene.String()
    columns = graphene.List(lambda: ColumnType)

    def resolve_columns(self, info):
        try:
            return [ColumnType(**column) for column in db.get_columns(self.id)]
        except Exception as e:
            logger.error(f"Error al resolver columns: {str(e)}")
            return []

class ColumnType(graphene.ObjectType):
    id = graphene.ID()
    type = graphene.String()
    name = graphene.String()
    order = graphene.Int()
    board_id = graphene.ID()
    created_at = graphene.String()
    updated_at = graphene.String()
    cards = graphene.List(lambda: CardType)

    def resolve_cards(self, info):
        try:
            cards = db.get_cards(self.id)
            # Convertir column_id a columnId para cada tarjeta
            for card in cards:
                if 'column_id' in card:
                    card['columnId'] = card['column_id']
                    del card['column_id']
            return [CardType(**card) for card in cards]
        except Exception as e:
            logger.error(f"Error al resolver cards: {str(e)}")
            return []

class CardType(graphene.ObjectType):
    id = graphene.ID()
    type = graphene.String()
    title = graphene.String()
    description = graphene.String()
    order = graphene.Int()
    columnId = graphene.ID()
    created_at = graphene.String()
    updated_at = graphene.String()

class Query(graphene.ObjectType):
    boards = graphene.List(BoardType)
    columns = graphene.List(ColumnType, board_id=graphene.ID())
    cards = graphene.List(CardType, column_id=graphene.ID())

    def resolve_boards(self, info):
        try:
            return [BoardType(**board) for board in db.get_boards()]
        except Exception as e:
            logger.error(f"Error al resolver boards: {str(e)}")
            return []

    def resolve_columns(self, info, board_id):
        try:
            return [ColumnType(**column) for column in db.get_columns(board_id)]
        except Exception as e:
            logger.error(f"Error al resolver columns: {str(e)}")
            return []

    def resolve_cards(self, info, column_id):
        try:
            return [CardType(**card) for card in db.get_cards(column_id)]
        except Exception as e:
            logger.error(f"Error al resolver cards: {str(e)}")
            return []

class CreateBoard(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        type = graphene.String(required=True)

    board = graphene.Field(BoardType)
    error = graphene.String()

    def mutate(self, info, name, type):
        try:
            logger.info(f"Intentando crear board con name={name}, type={type}")
            board_id = db.create_board(name, type)
            logger.info(f"Board creado con ID: {board_id}")
            
            # Obtener el tablero específico que acabamos de crear
            response = db.table.get_item(
                Key={
                    'id': board_id
                }
            )
            board_data = response.get('Item')
            
            if not board_data:
                error_msg = f"No se pudo encontrar el board con ID {board_id}"
                logger.error(error_msg)
                return CreateBoard(error=error_msg)
                
            logger.info(f"Board encontrado: {board_data}")
            # Convertir los datos de DynamoDB al formato esperado por BoardType
            board = {
                'id': board_data['id'],
                'type': board_data['type'],
                'name': board_data['name'],
                'created_at': board_data['created_at'],
                'updated_at': board_data['updated_at']
            }
            return CreateBoard(board=BoardType(**board))
        except Exception as e:
            error_msg = f"Error al crear board: {str(e)}"
            logger.error(error_msg)
            return CreateBoard(error=error_msg)

class UpdateBoard(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        name = graphene.String(required=True)

    board = graphene.Field(BoardType)
    error = graphene.String()

    def mutate(self, info, id, name):
        try:
            board = db.get_boards()[0]
            return UpdateBoard(board=BoardType(**board))
        except Exception as e:
            logger.error(f"Error al actualizar board: {str(e)}")
            return UpdateBoard(error=str(e))

class DeleteBoard(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    success = graphene.Boolean()
    error = graphene.String()

    def mutate(self, info, id):
        try:
            return DeleteBoard(success=True)
        except Exception as e:
            logger.error(f"Error al eliminar board: {str(e)}")
            return DeleteBoard(success=False, error=str(e))

class CreateColumn(graphene.Mutation):
    class Arguments:
        boardId = graphene.ID(required=True)
        name = graphene.String(required=True)
        order = graphene.Int()

    column = graphene.Field(ColumnType)
    error = graphene.String()

    def mutate(self, info, boardId, name, order=None):
        try:
            column_id = db.create_column(boardId, name, order)
            column = db.get_columns(boardId)[-1]
            return CreateColumn(column=ColumnType(**column))
        except Exception as e:
            logger.error(f"Error al crear column: {str(e)}")
            return CreateColumn(error=str(e))

class UpdateColumn(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        name = graphene.String(required=True)
        order = graphene.Int()

    column = graphene.Field(ColumnType)
    error = graphene.String()

    def mutate(self, info, id, name, order=None):
        try:
            column = db.get_columns(id)[0]
            return UpdateColumn(column=ColumnType(**column))
        except Exception as e:
            logger.error(f"Error al actualizar column: {str(e)}")
            return UpdateColumn(error=str(e))

class DeleteColumn(graphene.Mutation):
    class Arguments:
        columnId = graphene.String(required=True)

    success = graphene.Boolean()
    columnId = graphene.String()
    error = graphene.String()

    def mutate(self, info, columnId):
        try:
            success = db.delete_column(columnId)
            if not success:
                return DeleteColumn(success=False, error="No se pudo eliminar la columna")
            return DeleteColumn(success=True, columnId=columnId)
        except Exception as e:
            logger.error(f"Error al eliminar columna: {str(e)}")
            return DeleteColumn(success=False, error=str(e))

class CreateCard(graphene.Mutation):
    class Arguments:
        columnId = graphene.ID(required=True)
        title = graphene.String(required=True)
        description = graphene.String()
        order = graphene.Int()

    card = graphene.Field(CardType)
    error = graphene.String()

    def mutate(self, info, columnId, title, description=None, order=None):
        try:
            card_id = db.create_card(columnId, title, description, order)
            if not card_id:
                error_msg = "No se pudo crear la tarjeta"
                logger.error(error_msg)
                return CreateCard(error=error_msg)
            
            # Obtener la tarjeta recién creada
            response = db.table.get_item(
                Key={
                    'id': card_id,
                    'type': 'card'
                }
            )
            card_data = response.get('Item')
            
            if not card_data:
                error_msg = f"No se pudo encontrar la tarjeta con ID {card_id}"
                logger.error(error_msg)
                return CreateCard(error=error_msg)
                
            logger.info(f"Tarjeta encontrada: {card_data}")
            # Convertir column_id a columnId
            if 'column_id' in card_data:
                card_data['columnId'] = card_data['column_id']
                del card_data['column_id']
            return CreateCard(card=CardType(**card_data))
        except Exception as e:
            error_msg = f"Error al crear tarjeta: {str(e)}"
            logger.error(error_msg)
            return CreateCard(error=error_msg)

class UpdateCard(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        title = graphene.String(required=True)
        description = graphene.String()

    card = graphene.Field(CardType)
    error = graphene.String()

    def mutate(self, info, id, title, description=None):
        try:
            updated_card = db.update_card(id, title, description)
            if not updated_card:
                return UpdateCard(error="No se pudo actualizar la tarjeta")
            # Convertir column_id a columnId
            if 'column_id' in updated_card:
                updated_card['columnId'] = updated_card['column_id']
                del updated_card['column_id']
            return UpdateCard(card=CardType(**updated_card))
        except Exception as e:
            logger.error(f"Error al actualizar card: {str(e)}")
            return UpdateCard(error=str(e))

class DeleteCard(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    success = graphene.Boolean()
    error = graphene.String()

    def mutate(self, info, id):
        try:
            success = db.delete_card(id)
            return DeleteCard(success=success)
        except Exception as e:
            logger.error(f"Error al eliminar card: {str(e)}")
            return DeleteCard(success=False, error=str(e))

class MoveCard(graphene.Mutation):
    class Arguments:
        cardId = graphene.String(required=True)
        columnId = graphene.String(required=True)
        cardOrder = graphene.Int(required=True)

    card = graphene.Field(CardType)
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info, cardId: str, columnId: str, cardOrder: int):
        try:
            logger.info(f"Intentando mover tarjeta: cardId={cardId}, columnId={columnId}, cardOrder={cardOrder}")
            updated_card = db.move_card(str(cardId), str(columnId), int(cardOrder))
            
            if not updated_card:
                return MoveCard(success=False, message="No se pudo mover la tarjeta")
            
            # Convertir column_id a columnId para mantener consistencia con el frontend
            card_data = {
                'id': updated_card['id'],
                'title': updated_card['title'],
                'description': updated_card.get('description', ''),
                'columnId': updated_card['column_id'],
                'order': updated_card['order'],
                'created_at': updated_card['created_at'],
                'updated_at': updated_card['updated_at']
            }
            
            return MoveCard(
                card=CardType(**card_data),
                success=True,
                message="Tarjeta movida exitosamente"
            )
        except Exception as e:
            logger.error(f"Error en mutación MoveCard: {str(e)}")
            return MoveCard(success=False, message=str(e))

class MoveColumn(graphene.Mutation):
    class Arguments:
        columnId = graphene.ID(required=True)
        order = graphene.Int(required=True)

    success = graphene.Boolean()
    error = graphene.String()

    def mutate(self, info, columnId, order):
        try:
            updated_column = db.move_column(columnId, order)
            if not updated_column:
                error_msg = f"No se pudo mover la columna con ID {columnId}"
                logger.error(error_msg)
                return MoveColumn(success=False, error=error_msg)
            
            logger.info(f"Columna movida: {updated_column}")
            return MoveColumn(success=True)
        except Exception as e:
            error_msg = f"Error al mover columna: {str(e)}"
            logger.error(error_msg)
            return MoveColumn(success=False, error=error_msg)

class FixCardOrders(graphene.Mutation):
    success = graphene.Boolean()
    error = graphene.String()

    def mutate(self, info):
        try:
            db.fix_card_orders()
            return FixCardOrders(success=True)
        except Exception as e:
            error_msg = f"Error al arreglar el orden de las tarjetas: {str(e)}"
            logger.error(error_msg)
            return FixCardOrders(success=False, error=error_msg)

class Mutation(graphene.ObjectType):
    create_board = CreateBoard.Field()
    update_board = UpdateBoard.Field()
    delete_board = DeleteBoard.Field()
    create_column = CreateColumn.Field()
    update_column = UpdateColumn.Field()
    delete_column = DeleteColumn.Field()
    create_card = CreateCard.Field()
    update_card = UpdateCard.Field()
    delete_card = DeleteCard.Field()
    move_card = MoveCard.Field()
    move_column = MoveColumn.Field()
    fix_card_orders = FixCardOrders.Field()

schema = graphene.Schema(query=Query, mutation=Mutation) 