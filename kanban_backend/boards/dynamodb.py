import boto3
import os
import uuid
from datetime import datetime
import logging
import time
from typing import Optional, Dict

logger = logging.getLogger(__name__)

class DynamoDBAdapter:
    def __init__(self):
        self.table_name = os.getenv('DYNAMODB_TABLE_NAME', 'kanban_board')
        self.endpoint_url = os.getenv('DYNAMODB_ENDPOINT', 'http://localhost:8002')
        self.region = os.getenv('AWS_DEFAULT_REGION', 'us-west-2')
        self.access_key = os.getenv('AWS_ACCESS_KEY_ID', 'local')
        self.secret_key = os.getenv('AWS_SECRET_ACCESS_KEY', 'local')

        try:
            self.dynamodb = boto3.resource(
                'dynamodb',
                endpoint_url=self.endpoint_url,
                region_name=self.region,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key
            )

            self.table = self.dynamodb.Table(self.table_name)
            self._create_table_if_not_exists()
        except Exception as e:
            logger.error(f"Error al inicializar DynamoDB: {str(e)}")
            raise

    def _create_table_if_not_exists(self):
        try:
            self.table.load()
            logger.info(f"Tabla {self.table_name} ya existe")
        except self.dynamodb.meta.client.exceptions.ResourceNotFoundException:
            logger.info(f"Creando tabla {self.table_name}")
            try:
                # Crear la tabla
                self.dynamodb.create_table(
                    TableName=self.table_name,
                    KeySchema=[
                        {'AttributeName': 'id', 'KeyType': 'HASH'}
                    ],
                    AttributeDefinitions=[
                        {'AttributeName': 'id', 'AttributeType': 'S'},
                        {'AttributeName': 'type', 'AttributeType': 'S'},
                        {'AttributeName': 'column_id', 'AttributeType': 'S'},
                        {'AttributeName': 'board_id', 'AttributeType': 'S'}
                    ],
                    GlobalSecondaryIndexes=[
                        {
                            'IndexName': 'TypeIndex',
                            'KeySchema': [
                                {'AttributeName': 'type', 'KeyType': 'HASH'}
                            ],
                            'Projection': {
                                'ProjectionType': 'ALL'
                            },
                            'ProvisionedThroughput': {
                                'ReadCapacityUnits': 5,
                                'WriteCapacityUnits': 5
                            }
                        },
                        {
                            'IndexName': 'ColumnIdIndex',
                            'KeySchema': [
                                {'AttributeName': 'column_id', 'KeyType': 'HASH'},
                                {'AttributeName': 'type', 'KeyType': 'RANGE'}
                            ],
                            'Projection': {
                                'ProjectionType': 'ALL'
                            },
                            'ProvisionedThroughput': {
                                'ReadCapacityUnits': 5,
                                'WriteCapacityUnits': 5
                            }
                        },
                        {
                            'IndexName': 'BoardIdIndex',
                            'KeySchema': [
                                {'AttributeName': 'board_id', 'KeyType': 'HASH'},
                                {'AttributeName': 'type', 'KeyType': 'RANGE'}
                            ],
                            'Projection': {
                                'ProjectionType': 'ALL'
                            },
                            'ProvisionedThroughput': {
                                'ReadCapacityUnits': 5,
                                'WriteCapacityUnits': 5
                            }
                        }
                    ],
                    ProvisionedThroughput={
                        'ReadCapacityUnits': 5,
                        'WriteCapacityUnits': 5
                    }
                )
                
                # Esperar a que la tabla esté completamente creada
                max_attempts = 30  # 30 intentos de 1 segundo = 30 segundos máximo
                for attempt in range(max_attempts):
                    try:
                        self.table.wait_until_exists()
                        logger.info(f"Tabla {self.table_name} creada exitosamente")
                        break
                    except Exception as e:
                        if attempt == max_attempts - 1:
                            raise Exception(f"Timeout esperando a que la tabla {self.table_name} se cree: {str(e)}")
                        logger.warning(f"Intento {attempt + 1} de esperar a que la tabla se cree: {str(e)}")
                        time.sleep(1)
                
                # Verificar que los índices estén activos
                for index_name in ['TypeIndex', 'ColumnIdIndex', 'BoardIdIndex']:
                    for attempt in range(max_attempts):
                        try:
                            response = self.dynamodb.meta.client.describe_table(
                                TableName=self.table_name
                            )
                            index_status = next(
                                (idx['IndexStatus'] for idx in response['Table']['GlobalSecondaryIndexes']
                                 if idx['IndexName'] == index_name),
                                None
                            )
                            if index_status == 'ACTIVE':
                                logger.info(f"Índice {index_name} está activo")
                                break
                            elif attempt == max_attempts - 1:
                                raise Exception(f"Timeout esperando a que el índice {index_name} se active")
                            else:
                                logger.warning(f"Índice {index_name} aún no está activo, intento {attempt + 1}")
                                time.sleep(1)
                        except Exception as e:
                            if attempt == max_attempts - 1:
                                raise Exception(f"Error verificando el índice {index_name}: {str(e)}")
                            logger.warning(f"Error verificando el índice {index_name}, intento {attempt + 1}: {str(e)}")
                            time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error al crear tabla {self.table_name}: {str(e)}")
                raise

    def get_boards(self):
        try:
            response = self.table.query(
                IndexName='TypeIndex',
                KeyConditionExpression='#t = :type',
                ExpressionAttributeNames={
                    '#t': 'type'
                },
                ExpressionAttributeValues={
                    ':type': 'board'
                }
            )
            boards = response.get('Items', [])
            logger.info(f"Boards encontrados: {len(boards)}")
            for board in boards:
                logger.info(f"Board: {board}")
            return boards
        except Exception as e:
            logger.error(f"Error al obtener boards: {str(e)}")
            raise

    def create_board(self, name, type='board'):
        try:
            # Primero verificar si ya existe un tablero
            existing_boards = self.get_boards()
            if existing_boards:
                logger.info("Ya existe un tablero, retornando el primero encontrado")
                return existing_boards[0]['id']

            # Si no existe, crear uno nuevo
            board_id = str(uuid.uuid4())
            now = datetime.utcnow().isoformat()
            item = {
                'id': board_id,
                'type': type,
                'name': name,
                'created_at': now,
                'updated_at': now
            }
            logger.info(f"Creando board con item: {item}")
            
            # Intentar crear el board hasta 3 veces si falla
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = self.table.put_item(
                        Item=item,
                        ReturnConsumedCapacity='TOTAL'
                    )
                    logger.info(f"Board creado. Consumo de capacidad: {response['ConsumedCapacity']}")
                    break
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    logger.warning(f"Intento {attempt + 1} fallido al crear board: {str(e)}")
                    time.sleep(1)  # Esperar 1 segundo antes de reintentar
            
            # Crear columnas por defecto
            columns = [
                ("Por Hacer", 0),
                ("En Progreso", 1),
                ("Completado", 2)
            ]
            
            for column_name, order in columns:
                try:
                    self.create_column(board_id, column_name, order)
                    logger.info(f"Columna '{column_name}' creada para el board {board_id}")
                except Exception as e:
                    logger.error(f"Error al crear columna '{column_name}': {str(e)}")
                    # Continuar con las siguientes columnas aunque falle una
            
            return board_id
        except Exception as e:
            logger.error(f"Error al crear board: {str(e)}")
            raise

    def get_columns(self, board_id):
        try:
            response = self.table.query(
                IndexName='BoardIdIndex',
                KeyConditionExpression='board_id = :board_id AND #t = :type',
                ExpressionAttributeNames={
                    '#t': 'type'
                },
                ExpressionAttributeValues={
                    ':board_id': board_id,
                    ':type': 'column'
                }
            )
            return response.get('Items', [])
        except Exception as e:
            logger.error(f"Error al obtener columns: {str(e)}")
            raise

    def create_column(self, board_id, name, order=None):
        try:
            column_id = str(uuid.uuid4())
            now = datetime.utcnow().isoformat()
            self.table.put_item(
                Item={
                    'id': column_id,
                    'type': 'column',
                    'board_id': board_id,
                    'name': name,
                    'order': order or 0,
                    'created_at': now,
                    'updated_at': now
                }
            )
            return column_id
        except Exception as e:
            logger.error(f"Error al crear column: {str(e)}")
            raise

    def get_cards(self, column_id):
        try:
            response = self.table.query(
                IndexName='ColumnIdIndex',
                KeyConditionExpression='column_id = :column_id AND #t = :type',
                ExpressionAttributeNames={
                    '#t': 'type'
                },
                ExpressionAttributeValues={
                    ':column_id': column_id,
                    ':type': 'card'
                }
            )
            return response.get('Items', [])
        except Exception as e:
            logger.error(f"Error al obtener cards: {str(e)}")
            raise

    def create_card(self, column_id, title, description='', order=None):
        try:
            # Verificar si ya existe una tarjeta con el mismo título en la columna
            cards = self.get_cards(column_id)
            for card in cards:
                if card.get('title') == title:
                    raise Exception(f"Ya existe una tarjeta con el título '{title}' en esta columna")

            # Si no se proporciona un orden, usar el número de tarjetas existentes
            if order is None:
                order = len(cards)

            card_id = str(uuid.uuid4())
            now = datetime.utcnow().isoformat()
            item = {
                'id': card_id,
                'type': 'card',
                'column_id': column_id,
                'title': title,
                'description': description,
                'order': order,  # Asegurar que el orden siempre tenga un valor
                'created_at': now,
                'updated_at': now
            }
            
            # Actualizar el orden de las tarjetas existentes
            with self.table.batch_writer() as batch:
                # Primero, actualizar el orden de las tarjetas existentes
                for i, existing_card in enumerate(cards):
                    if i >= order:
                        batch.put_item(Item={
                            **existing_card,
                            'order': i + 1,
                            'updated_at': now
                        })
                
                # Luego, crear la nueva tarjeta
                batch.put_item(Item=item)

            logger.info(f"Tarjeta creada: {item}")
            return card_id
        except Exception as e:
            logger.error(f"Error al crear tarjeta: {str(e)}")
            raise

    def update_card(self, card_id, title, description=None):
        try:
            # Primero obtener el card existente
            response = self.table.get_item(
                Key={
                    'id': card_id,
                    'type': 'card'
                }
            )
            card = response.get('Item')
            if not card:
                raise Exception(f"No se encontró el card con ID {card_id}")

            # Actualizar los campos manteniendo todos los valores existentes
            now = datetime.utcnow().isoformat()
            update_expression = "SET title = :title, description = :description, updated_at = :updated_at"
            expression_values = {
                ':title': title,
                ':description': description or '',
                ':updated_at': now
            }

            # Mantener todos los campos existentes excepto type
            for key, value in card.items():
                if key not in ['title', 'description', 'updated_at', 'type']:
                    update_expression += f", {key} = :{key}"
                    expression_values[f':{key}'] = value

            response = self.table.update_item(
                Key={
                    'id': card_id,
                    'type': 'card'
                },
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_values,
                ReturnValues='ALL_NEW'
            )

            updated_card = response.get('Attributes')
            # Asegurarnos de que el type se mantiene
            updated_card['type'] = 'card'
            logger.info(f"Card actualizado: {updated_card}")
            return updated_card
        except Exception as e:
            logger.error(f"Error al actualizar card: {str(e)}")
            raise

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

            # Actualizar las tarjetas para mantener su orden
            for index, card in enumerate(cards):
                try:
                    self.table.update_item(
                        Key={
                            'id': card['id'],
                            'type': 'card'
                        },
                        UpdateExpression="SET #o = :order, updated_at = :updated_at",
                        ExpressionAttributeValues={
                            ':order': index,
                            ':updated_at': now
                        },
                        ExpressionAttributeNames={
                            '#o': 'order'
                        }
                    )
                    logger.info(f"Tarjeta {card['id']} actualizada con orden {index}")
                except Exception as e:
                    logger.error(f"Error al actualizar tarjeta {card['id']}: {str(e)}")
                    raise

            return {'id': column_id, 'type': 'column', 'order': new_order, 'board_id': board_id}
        except Exception as e:
            logger.error(f"Error al mover columna: {str(e)}")
            raise

    def delete_card(self, card_id):
        """
        Elimina una tarjeta por su ID.
        """
        try:
            # Primero verificar que la tarjeta existe
            response = self.table.get_item(
                Key={
                    'id': card_id
                }
            )
            card = response.get('Item')
            if not card or card.get('type') != 'card':
                raise Exception(f"No se encontró la tarjeta con ID {card_id}")

            # Eliminar la tarjeta
            response = self.table.delete_item(
                Key={
                    'id': card_id
                },
                ReturnValues='ALL_OLD'
            )
            
            deleted_card = response.get('Attributes')
            logger.info(f"Tarjeta eliminada: {deleted_card}")
            return True
        except Exception as e:
            logger.error(f"Error al eliminar tarjeta: {str(e)}")
            raise

    def delete_column(self, column_id):
        try:
            # Verificar si la columna existe
            response = self.table.get_item(
                Key={'id': column_id}
            )
            column = response.get('Item')
            if not column or column.get('type') != 'column':
                raise Exception(f"No se encontró la columna con ID {column_id}")

            # Obtener el board_id de la columna
            board_id = column.get('board_id')
            if not board_id:
                raise Exception(f"La columna {column_id} no tiene un board_id asociado")

            # Obtener todas las columnas del board
            columns = self.get_columns(board_id)
            if not columns:
                raise Exception(f"No se encontraron columnas para el board {board_id}")

            # Encontrar la primera columna disponible (diferente a la que se va a eliminar)
            target_column = next((col for col in columns if col['id'] != column_id), None)
            if not target_column:
                raise Exception("No hay columnas disponibles para mover las tarjetas")

            # Obtener todas las tarjetas de la columna a eliminar
            cards = self.get_cards(column_id)
            logger.info(f"Tarjetas encontradas en la columna: {len(cards)}")

            # Mover cada tarjeta a la columna destino
            for card in cards:
                try:
                    # Obtener el número de tarjetas en la columna destino
                    target_cards = self.get_cards(target_column['id'])
                    new_order = len(target_cards)

                    # Actualizar la tarjeta con la nueva columna y orden
                    self.table.update_item(
                        Key={'id': card['id']},
                        UpdateExpression="SET column_id = :column_id, #o = :order, updated_at = :updated_at",
                        ExpressionAttributeValues={
                            ':column_id': target_column['id'],
                            ':order': new_order,
                            ':updated_at': datetime.utcnow().isoformat()
                        },
                        ExpressionAttributeNames={'#o': 'order'}
                    )
                    logger.info(f"Tarjeta {card['id']} movida a la columna {target_column['id']}")
                except Exception as e:
                    logger.error(f"Error al mover tarjeta {card['id']}: {str(e)}")
                    raise

            # Eliminar la columna
            response = self.table.delete_item(
                Key={'id': column_id},
                ReturnValues='ALL_OLD'
            )
            
            deleted_column = response.get('Attributes')
            logger.info(f"Columna eliminada: {deleted_column}")
            return True
        except Exception as e:
            logger.error(f"Error al eliminar columna: {str(e)}")
            raise

    def get_card(self, card_id: str) -> Optional[Dict]:
        try:
            response = self.table.get_item(
                Key={
                    'id': card_id
                }
            )
            card = response.get('Item')
            if card and card.get('type') == 'card':
                return card
            return None
        except Exception as e:
            logger.error(f"Error al obtener card {card_id}: {str(e)}")
            return None

    def move_card(self, card_id: str, column_id: str, card_order: int) -> Optional[Dict]:
        try:
            # Obtener la tarjeta actual
            card = self.get_card(card_id)
            if not card:
                logger.error(f"Card {card_id} not found")
                return None

            # Obtener el column_id actual
            current_column_id = card.get('column_id')
            
            # Si la tarjeta ya está en la columna destino y tiene el mismo orden, no hacer nada
            if current_column_id == column_id and card.get('order') == card_order:
                return card

            # Obtener todas las tarjetas de la columna destino
            dest_cards = self.get_cards(column_id)
            dest_cards.sort(key=lambda x: x.get('order', 0))

            # Si la tarjeta se está moviendo a una columna diferente
            if current_column_id != column_id:
                # Obtener todas las tarjetas de la columna origen
                source_cards = self.get_cards(current_column_id)
                source_cards.sort(key=lambda x: x.get('order', 0))

                # Remover la tarjeta de la columna origen
                source_cards = [c for c in source_cards if c['id'] != card_id]
                
                # Reordenar las tarjetas en la columna origen
                for index, c in enumerate(source_cards):
                    self.table.update_item(
                        Key={'id': c['id']},
                        UpdateExpression="SET #o = :order, updated_at = :updated_at",
                        ExpressionAttributeValues={
                            ':order': index,
                            ':updated_at': datetime.utcnow().isoformat()
                        },
                        ExpressionAttributeNames={'#o': 'order'}
                    )

            # Insertar la tarjeta en la nueva posición
            dest_cards.insert(card_order, card)
            
            # Reordenar todas las tarjetas en la columna destino
            for index, c in enumerate(dest_cards):
                self.table.update_item(
                    Key={'id': c['id']},
                    UpdateExpression="SET column_id = :column_id, #o = :order, updated_at = :updated_at",
                    ExpressionAttributeValues={
                        ':column_id': column_id,
                        ':order': index,
                        ':updated_at': datetime.utcnow().isoformat()
                    },
                    ExpressionAttributeNames={'#o': 'order'}
                )

            # Obtener la tarjeta actualizada
            updated_card = self.get_card(card_id)
            return updated_card

        except Exception as e:
            logger.error(f"Error moving card {card_id}: {str(e)}")
            return None

    def _reorder_cards_in_column(self, column_id: str):
        """Reordena las tarjetas en una columna específica."""
        try:
            # Obtener todas las tarjetas de la columna
            cards = self.get_cards(column_id)
            if not cards:
                return

            # Ordenar las tarjetas por su orden actual
            cards.sort(key=lambda x: x.get('order', 0))

            # Actualizar el orden de cada tarjeta
            for index, card in enumerate(cards):
                self.table.update_item(
                    Key={
                        'id': card['id']
                    },
                    UpdateExpression="SET #o = :order, updated_at = :updated_at",
                    ExpressionAttributeValues={
                        ':order': index,
                        ':updated_at': datetime.utcnow().isoformat()
                    },
                    ExpressionAttributeNames={
                        '#o': 'order'
                    }
                )
        except Exception as e:
            logger.error(f"Error reordering cards in column {column_id}: {str(e)}")

    def fix_card_orders(self):
        """
        Actualiza el orden de todas las tarjetas que tienen order: NULL
        """
        try:
            # Obtener todas las columnas
            columns = self.table.query(
                IndexName='TypeIndex',
                KeyConditionExpression='#t = :type',
                ExpressionAttributeNames={
                    '#t': 'type'
                },
                ExpressionAttributeValues={
                    ':type': 'column'
                }
            ).get('Items', [])

            now = datetime.utcnow().isoformat()

            # Para cada columna, actualizar el orden de sus tarjetas
            for column in columns:
                column_id = column['id']
                cards = self.get_cards(column_id)
                
                # Ordenar las tarjetas por fecha de creación si no tienen orden
                cards.sort(key=lambda x: x.get('created_at', ''))
                
                # Actualizar el orden de todas las tarjetas
                with self.table.batch_writer() as batch:
                    for index, card in enumerate(cards):
                        if card.get('order') is None:
                            batch.put_item(Item={
                                **card,
                                'order': index,
                                'updated_at': now
                            })

            return True
        except Exception as e:
            logger.error(f"Error al actualizar el orden de las tarjetas: {str(e)}")
            raise 