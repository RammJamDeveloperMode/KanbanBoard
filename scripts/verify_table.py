import boto3
import os
import time

def verify_table():
    # Configuración de DynamoDB
    dynamodb = boto3.resource(
        'dynamodb',
        endpoint_url='http://localhost:8002',
        region_name='us-west-2',
        aws_access_key_id='local',
        aws_secret_access_key='local'
    )

    table_name = 'kanban_board'

    try:
        # Verificar si la tabla existe
        table = dynamodb.Table(table_name)
        table.load()
        print(f"La tabla {table_name} ya existe")
    except dynamodb.meta.client.exceptions.ResourceNotFoundException:
        print(f"La tabla {table_name} no existe. Creándola...")
        # Crear la tabla
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
        table.wait_until_exists()
        print(f"Tabla {table_name} creada exitosamente")

if __name__ == '__main__':
    verify_table() 