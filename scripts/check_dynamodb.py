import boto3
from botocore.config import Config
import json

def check_dynamodb():
    # Configurar el cliente de DynamoDB
    dynamodb = boto3.resource(
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
    
    # Obtener la tabla
    table = dynamodb.Table('kanban_board')
    
    # Escanear todos los elementos
    response = table.scan()
    items = response.get('Items', [])
    
    # Imprimir los resultados de forma organizada
    print("\n=== Contenido de DynamoDB ===")
    
    # Agrupar por tipo
    boards = [item for item in items if item['type'] == 'board']
    columns = [item for item in items if item['type'] == 'column']
    cards = [item for item in items if item['type'] == 'card']
    
    print(f"\nTableros ({len(boards)}):")
    for board in boards:
        print(f"- {board['name']} (ID: {board['id']})")
    
    print(f"\nColumnas ({len(columns)}):")
    for column in columns:
        print(f"- {column['name']} (ID: {column['id']}, Board: {column['board_id']})")
    
    print(f"\nTarjetas ({len(cards)}):")
    for card in cards:
        print(f"- {card['title']} (ID: {card['id']}, Columna: {card['column_id']})")

if __name__ == '__main__':
    check_dynamodb() 