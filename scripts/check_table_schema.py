import boto3
import os
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_table_schema():
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
        
        try:
            # Obtener la descripción de la tabla
            table = dynamodb.Table(table_name)
            response = table.meta.client.describe_table(TableName=table_name)
            
            # Mostrar información de la tabla
            logger.info("=== Información de la tabla ===")
            logger.info(f"Nombre de la tabla: {table_name}")
            logger.info(f"Estado: {response['Table']['TableStatus']}")
            
            # Mostrar esquema de claves
            logger.info("\n=== Esquema de claves ===")
            for key in response['Table']['KeySchema']:
                logger.info(f"Clave: {key['AttributeName']}, Tipo: {key['KeyType']}")
            
            # Mostrar definiciones de atributos
            logger.info("\n=== Definiciones de atributos ===")
            for attr in response['Table']['AttributeDefinitions']:
                logger.info(f"Atributo: {attr['AttributeName']}, Tipo: {attr['AttributeType']}")
            
            # Mostrar índices secundarios si existen
            if 'GlobalSecondaryIndexes' in response['Table']:
                logger.info("\n=== Índices secundarios ===")
                for index in response['Table']['GlobalSecondaryIndexes']:
                    logger.info(f"Índice: {index['IndexName']}")
                    for key in index['KeySchema']:
                        logger.info(f"  Clave: {key['AttributeName']}, Tipo: {key['KeyType']}")
            
        except dynamodb.meta.client.exceptions.ResourceNotFoundException:
            logger.error(f"La tabla {table_name} no existe")
        except Exception as e:
            logger.error(f"Error al obtener información de la tabla: {str(e)}")
            
    except Exception as e:
        logger.error(f"Error general: {str(e)}")

if __name__ == "__main__":
    check_table_schema() 