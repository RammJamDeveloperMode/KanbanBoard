import boto3
import os
from botocore.config import Config
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def reset_dynamodb():
    # Configurar el cliente de DynamoDB
    dynamodb = boto3.resource(
        'dynamodb',
        endpoint_url='http://localhost:8002',
        region_name='us-west-2',
        aws_access_key_id='local',
        aws_secret_access_key='local',
        config=Config(
            retries=dict(
                max_attempts=10
            )
        )
    )
    
    # Nombre de la tabla
    table_name = 'kanban_board'
    
    try:
        # Eliminar la tabla si existe
        try:
            table = dynamodb.Table(table_name)
            table.delete()
            logger.info(f"Tabla {table_name} eliminada")
            
            # Esperar a que la tabla se elimine
            waiter = dynamodb.meta.client.get_waiter('table_not_exists')
            waiter.wait(TableName=table_name)
        except dynamodb.meta.client.exceptions.ResourceNotFoundException:
            logger.info(f"Tabla {table_name} no existe, procediendo a crear")
        
        # Crear la tabla con el nuevo esquema
        logger.info("Creando tabla con el siguiente esquema:")
        logger.info("Clave de partición: id (String)")
        logger.info("Clave de ordenación: kind (String)")
        
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {'AttributeName': 'id', 'KeyType': 'HASH'},
                {'AttributeName': 'kind', 'KeyType': 'RANGE'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'id', 'AttributeType': 'S'},
                {'AttributeName': 'kind', 'AttributeType': 'S'}
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        
        # Esperar a que la tabla esté activa
        waiter = dynamodb.meta.client.get_waiter('table_exists')
        waiter.wait(TableName=table_name)
        
        # Verificar el esquema de la tabla
        table_description = table.meta.client.describe_table(TableName=table_name)
        logger.info("Esquema de la tabla creada:")
        logger.info(f"Claves: {table_description['Table']['KeySchema']}")
        logger.info(f"Atributos: {table_description['Table']['AttributeDefinitions']}")
        
        logger.info(f"Tabla {table_name} creada con éxito")
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise

if __name__ == "__main__":
    reset_dynamodb() 