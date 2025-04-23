import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
import json
from datetime import datetime
import uuid
from typing import List, Dict, Any, Optional

class DynamoDBAdapter:
    def __init__(self):
        self.dynamodb = boto3.resource(
            'dynamodb',
            endpoint_url='http://localhost:8002',
            region_name='us-west-2',
            aws_access_key_id='fakeMyKeyId',
            aws_secret_access_key='fakeSecretAccessKey',
            config=Config(
                retries=dict(
                    max_attempts=10
                )
            )
        )
        try:
            self.table = self.dynamodb.Table('kanban_board')
            # Verificar si la tabla existe
            self.table.table_status
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                # Si la tabla no existe, la creamos
                self.dynamodb.create_table(
                    TableName='kanban_board',
                    KeySchema=[
                        {'AttributeName': 'id', 'KeyType': 'HASH'},
                        {'AttributeName': 'type', 'KeyType': 'RANGE'}
                    ],
                    AttributeDefinitions=[
                        {'AttributeName': 'id', 'AttributeType': 'S'},
                        {'AttributeName': 'type', 'AttributeType': 'S'}
                    ],
                    ProvisionedThroughput={
                        'ReadCapacityUnits': 5,
                        'WriteCapacityUnits': 5
                    }
                )
                # Esperar a que la tabla esté activa
                waiter = self.dynamodb.meta.client.get_waiter('table_exists')
                waiter.wait(TableName='kanban_board')
                self.table = self.dynamodb.Table('kanban_board')
            else:
                raise e

    def create_board(self, name):
        board_id = str(uuid.uuid4())
        item = {
            'id': board_id,
            'type': 'board',
            'name': name,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        self.table.put_item(Item=item)
        
        # Verificar si ya existen columnas para este board
        existing_columns = self.get_columns(board_id)
        if not existing_columns:
            # Crear columnas por defecto solo si no existen
            columns = [
                ("Por Hacer", 0),
                ("En Progreso", 1),
                ("Completado", 2)
            ]
            
            for column_name, order in columns:
                self.create_column(board_id, column_name, order)
            
        return board_id

    def create_column(self, board_id, name, order=0):
        column_id = str(uuid.uuid4())
        item = {
            'id': column_id,
            'type': 'column',
            'board_id': board_id,
            'name': name,
            'order': order,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        self.table.put_item(Item=item)
        return column_id

    def create_card(self, column_id, title, description='', order=0):
        card_id = str(uuid.uuid4())
        item = {
            'id': card_id,
            'type': 'card',
            'column_id': column_id,
            'title': title,
            'description': description,
            'order': order,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        self.table.put_item(Item=item)
        return card_id

    def get_boards(self):
        response = self.table.scan(
            FilterExpression='#type = :type',
            ExpressionAttributeNames={'#type': 'type'},
            ExpressionAttributeValues={':type': 'board'}
        )
        boards = response.get('Items', [])
        # Remover el campo type de cada board
        return [{k: v for k, v in board.items() if k != 'type'} for board in boards]

    def get_columns(self, board_id):
        response = self.table.scan(
            FilterExpression='#type = :type AND board_id = :board_id',
            ExpressionAttributeNames={'#type': 'type'},
            ExpressionAttributeValues={
                ':type': 'column',
                ':board_id': board_id
            }
        )
        columns = response.get('Items', [])
        # Remover el campo type de cada columna
        columns = [{k: v for k, v in column.items() if k != 'type'} for column in columns]
        # Ordenar columnas por su orden
        columns.sort(key=lambda x: x.get('order', 0))
        return columns

    def get_cards(self, column_id):
        response = self.table.scan(
            FilterExpression='#type = :type AND column_id = :column_id',
            ExpressionAttributeNames={'#type': 'type'},
            ExpressionAttributeValues={
                ':type': 'card',
                ':column_id': column_id
            }
        )
        cards = response.get('Items', [])
        # Remover el campo type de cada tarjeta
        return [{k: v for k, v in card.items() if k != 'type'} for card in cards]

    def update_card(self, card_id, **kwargs):
        update_expression = []
        expression_attribute_values = {}
        expression_attribute_names = {}

        for key, value in kwargs.items():
            if value is not None:
                update_expression.append(f'#{key} = :{key}')
                expression_attribute_names[f'#{key}'] = key
                expression_attribute_values[f':{key}'] = value

        if not update_expression:
            return None

        update_expression.append('#updated_at = :updated_at')
        expression_attribute_names['#updated_at'] = 'updated_at'
        expression_attribute_values[':updated_at'] = datetime.now().isoformat()

        try:
            response = self.table.update_item(
                Key={'id': card_id, 'type': 'card'},
                UpdateExpression='SET ' + ', '.join(update_expression),
                ExpressionAttributeNames=expression_attribute_names,
                ExpressionAttributeValues=expression_attribute_values,
                ReturnValues='ALL_NEW'
            )
            return response.get('Attributes')
        except ClientError as e:
            print(f"Error updating card: {e}")
            return None

    def delete_card(self, card_id):
        try:
            self.table.delete_item(
                Key={'id': card_id, 'type': 'card'}
            )
            return True
        except ClientError as e:
            print(f"Error deleting card: {e}")
            return False

    def delete_board(self, board_id):
        try:
            # Primero eliminar todas las columnas del board
            columns = self.get_columns(board_id)
            for column in columns:
                self.delete_column(column['id'])
                
            # Luego eliminar el board
            self.table.delete_item(
                Key={'id': board_id, 'type': 'board'}
            )
            return True
        except ClientError as e:
            print(f"Error deleting board: {e}")
            return False

    def delete_column(self, column_id):
        try:
            # Verificar si la columna existe
            response = self.table.get_item(
                Key={
                    'id': column_id,
                    'type': 'column'
                }
            )
            column = response.get('Item')
            if not column:
                raise Exception(f"No se encontró la columna con ID {column_id}")

            # Obtener todas las tarjetas de la columna
            cards = self.get_cards(column_id)
            logger.info(f"Tarjetas encontradas en la columna: {len(cards)}")

            # Eliminar todas las tarjetas en una transacción
            with self.table.batch_writer() as batch:
                for card in cards:
                    try:
                        batch.delete_item(
                            Key={
                                'id': card['id'],
                                'type': 'card'
                            }
                        )
                        logger.info(f"Tarjeta {card['id']} eliminada")
                    except Exception as e:
                        logger.error(f"Error al eliminar tarjeta {card['id']}: {str(e)}")
                        raise

            # Eliminar la columna
            self.table.delete_item(
                Key={
                    'id': column_id,
                    'type': 'column'
                }
            )
            logger.info(f"Columna {column_id} eliminada")
            return True
        except Exception as e:
            logger.error(f"Error al eliminar columna {column_id}: {str(e)}")
            return False

    def update_board(self, board_id, name):
        try:
            response = self.table.update_item(
                Key={'id': board_id, 'type': 'board'},
                UpdateExpression='SET #name = :name, #updated_at = :updated_at',
                ExpressionAttributeNames={
                    '#name': 'name',
                    '#updated_at': 'updated_at'
                },
                ExpressionAttributeValues={
                    ':name': name,
                    ':updated_at': datetime.now().isoformat()
                },
                ReturnValues='ALL_NEW'
            )
            return response.get('Attributes')
        except ClientError as e:
            print(f"Error updating board: {e}")
            return None

    def update_column(self, column_id, name, order=None):
        update_expression = ['SET #name = :name']
        expression_attribute_names = {'#name': 'name'}
        expression_attribute_values = {':name': name}

        if order is not None:
            update_expression.append('#order = :order')
            expression_attribute_names['#order'] = 'order'
            expression_attribute_values[':order'] = order

        update_expression.append('#updated_at = :updated_at')
        expression_attribute_names['#updated_at'] = 'updated_at'
        expression_attribute_values[':updated_at'] = datetime.now().isoformat()

        try:
            response = self.table.update_item(
                Key={'id': column_id, 'type': 'column'},
                UpdateExpression='SET ' + ', '.join(update_expression),
                ExpressionAttributeNames=expression_attribute_names,
                ExpressionAttributeValues=expression_attribute_values,
                ReturnValues='ALL_NEW'
            )
            return response.get('Attributes')
        except ClientError as e:
            print(f"Error updating column: {e}")
            return None

    def move_card(self, card_id, column_id):
        try:
            print(f"=== Iniciando move_card ===")
            print(f"card_id: {card_id} (tipo: {type(card_id)})")
            print(f"column_id: {column_id} (tipo: {type(column_id)})")
            
            # Verificar si la tarjeta existe
            card_response = self.table.get_item(
                Key={'id': card_id, 'type': 'card'}
            )
            print(f"Respuesta al obtener tarjeta: {card_response}")
            
            if 'Item' not in card_response:
                print(f"No se encontró la tarjeta con ID {card_id}")
                return None
                
            # Verificar si la columna existe
            column_response = self.table.get_item(
                Key={'id': column_id, 'type': 'column'}
            )
            print(f"Respuesta al obtener columna: {column_response}")
            
            if 'Item' not in column_response:
                print(f"No se encontró la columna con ID {column_id}")
                return None
                
            # Obtener todas las tarjetas de la columna destino
            cards_in_column = self.get_cards(column_id)
            next_order = len(cards_in_column)
                
            # Actualizar la tarjeta
            update_response = self.table.update_item(
                Key={'id': card_id, 'type': 'card'},
                UpdateExpression='SET #col_id = :col_id, #order = :order, #updated_at = :updated_at',
                ExpressionAttributeNames={
                    '#col_id': 'column_id',
                    '#order': 'order',
                    '#updated_at': 'updated_at'
                },
                ExpressionAttributeValues={
                    ':col_id': column_id,
                    ':order': next_order,
                    ':updated_at': datetime.now().isoformat()
                },
                ReturnValues='ALL_NEW'
            )
            print(f"Respuesta al actualizar tarjeta: {update_response}")
            
            if 'Attributes' not in update_response:
                print("Error: No se pudo actualizar la tarjeta")
                return None
                
            return update_response.get('Attributes')
            
        except ClientError as e:
            print(f"=== Error en move_card ===")
            print(f"Error: {str(e)}")
            print(f"Tipo de error: {type(e)}")
            print(f"Código de error: {e.response['Error']['Code']}")
            print(f"Mensaje de error: {e.response['Error']['Message']}")
            return None
        except Exception as e:
            print(f"=== Error inesperado en move_card ===")
            print(f"Error: {str(e)}")
            print(f"Tipo de error: {type(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return None 

    def move_column(self, column_id, new_order):
        try:
            # Obtener la columna actual
            response = self.table.get_item(
                Key={
                    'id': column_id,
                    'type': 'column'
                }
            )
            column = response.get('Item')
            if not column:
                raise Exception(f"No se encontró la columna con ID {column_id}")

            # Obtener el board_id de la columna
            board_id = column.get('board_id')
            if not board_id:
                raise Exception(f"La columna {column_id} no tiene un board_id asociado")

            # Obtener todas las columnas del board
            columns = self.get_columns(board_id)
            current_order = column.get('order', 0)

            # Preparar las actualizaciones para todas las columnas
            updates = []
            for col in columns:
                col_order = col.get('order', 0)
                if col['id'] == column_id:
                    # La columna que se está moviendo
                    updates.append({
                        'id': col['id'],
                        'type': 'column',
                        'order': new_order
                    })
                elif current_order < new_order:  # Moviendo hacia abajo
                    if current_order < col_order <= new_order:
                        updates.append({
                            'id': col['id'],
                            'type': 'column',
                            'order': col_order - 1
                        })
                else:  # Moviendo hacia arriba
                    if new_order <= col_order < current_order:
                        updates.append({
                            'id': col['id'],
                            'type': 'column',
                            'order': col_order + 1
                        })

            # Ejecutar todas las actualizaciones en una transacción
            with self.table.batch_writer() as batch:
                now = datetime.utcnow().isoformat()
                for update in updates:
                    batch.put_item(Item={
                        'id': update['id'],
                        'type': update['type'],
                        'order': update['order'],
                        'updated_at': now,
                        'board_id': board_id,
                        'name': next((col['name'] for col in columns if col['id'] == update['id']), '')
                    })

            # Obtener todas las tarjetas de la columna
            cards = self.get_cards(column_id)
            logger.info(f"Tarjetas encontradas en la columna: {len(cards)}")

            # Actualizar las tarjetas para mantener su orden y column_id
            for index, card in enumerate(cards):
                try:
                    self.table.update_item(
                        Key={
                            'id': card['id'],
                            'type': 'card'
                        },
                        UpdateExpression="SET #o = :order, #col_id = :column_id, updated_at = :updated_at",
                        ExpressionAttributeValues={
                            ':order': index,
                            ':column_id': column_id,
                            ':updated_at': now
                        },
                        ExpressionAttributeNames={
                            '#o': 'order',
                            '#col_id': 'column_id'
                        }
                    )
                    logger.info(f"Tarjeta {card['id']} actualizada con orden {index} y column_id {column_id}")
                except Exception as e:
                    logger.error(f"Error al actualizar tarjeta {card['id']}: {str(e)}")
                    raise

            return {'id': column_id, 'type': 'column', 'order': new_order, 'board_id': board_id}
            
        except ClientError as e:
            print(f"=== Error en move_column ===")
            print(f"Error: {str(e)}")
            print(f"Tipo de error: {type(e)}")
            print(f"Código de error: {e.response['Error']['Code']}")
            print(f"Mensaje de error: {e.response['Error']['Message']}")
            return None
        except Exception as e:
            print(f"=== Error inesperado en move_column ===")
            print(f"Error: {str(e)}")
            print(f"Tipo de error: {type(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return None 