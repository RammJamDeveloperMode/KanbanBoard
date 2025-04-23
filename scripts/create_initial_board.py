import boto3
import os
import uuid
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_initial_board():
    try:
        # Configurar cliente DynamoDB
        dynamodb = boto3.resource(
            'dynamodb',
            endpoint_url=os.getenv('DYNAMODB_ENDPOINT', 'http://localhost:8002'),
            region_name=os.getenv('AWS_DEFAULT_REGION', 'us-west-2'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID', 'local'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY', 'local')
        )

        table_name = os.getenv('DYNAMODB_TABLE_NAME', 'kanban_board')
        table = dynamodb.Table(table_name)

        # Verificar que la tabla existe
        try:
            table.load()
            logger.info(f"Tabla {table_name} existe y está activa")
        except Exception as e:
            logger.error(f"Error al verificar la tabla: {str(e)}")
            raise

        # Crear tablero inicial
        board_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        
        board_item = {
            'id': board_id,  # Clave de partición
            'kind': 'board',  # Clave de ordenación
            'name': 'Mi Tablero Kanban',
            'created_at': now,
            'updated_at': now
        }

        logger.info("Creando tablero...")
        logger.info(f"Item a insertar: {board_item}")
        
        # Verificar que el item tiene las claves requeridas
        if 'id' not in board_item or 'kind' not in board_item:
            raise ValueError("El item del tablero no tiene las claves 'id' y 'kind' requeridas")
            
        # Insertar el tablero
        response = table.put_item(
            Item=board_item,
            ReturnConsumedCapacity='TOTAL'
        )
        logger.info(f"Tablero creado con ID: {board_id}")
        logger.info(f"Consumo de capacidad: {response['ConsumedCapacity']}")

        # Crear columnas iniciales
        columns = [
            {'name': 'Por Hacer', 'order': 1},
            {'name': 'En Progreso', 'order': 2},
            {'name': 'Hecho', 'order': 3}
        ]

        for column in columns:
            column_id = str(uuid.uuid4())
            column_item = {
                'id': column_id,  # Clave de partición
                'kind': 'column',  # Clave de ordenación
                'name': column['name'],
                'board_id': board_id,
                'order': column['order'],
                'created_at': now,
                'updated_at': now
            }
            
            logger.info(f"Creando columna: {column['name']}")
            logger.info(f"Item a insertar: {column_item}")
            
            # Verificar que el item tiene las claves requeridas
            if 'id' not in column_item or 'kind' not in column_item:
                raise ValueError("El item de la columna no tiene las claves 'id' y 'kind' requeridas")
                
            # Insertar la columna
            response = table.put_item(
                Item=column_item,
                ReturnConsumedCapacity='TOTAL'
            )
            logger.info(f"Columna creada con ID: {column_id}")
            logger.info(f"Consumo de capacidad: {response['ConsumedCapacity']}")

        logger.info("Tablero y columnas creados exitosamente")

    except Exception as e:
        logger.error(f"Error al crear el tablero inicial: {str(e)}")
        raise

if __name__ == "__main__":
    create_initial_board() 