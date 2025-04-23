import boto3
from botocore.config import Config
import json
from decimal import Decimal

def scan_table():
    # Configurar el cliente de DynamoDB
    dynamodb = boto3.resource(
        'dynamodb',
        endpoint_url='http://localhost:8002',
        region_name='us-west-2',
        aws_access_key_id='dummy',
        aws_secret_access_key='dummy',
        config=Config(
            retries=dict(
                max_attempts=10
            )
        )
    )
    
    # Obtener la tabla
    table = dynamodb.Table('kanban_board')
    
    # Escanear la tabla
    response = table.scan()
    
    # Función para convertir Decimal a float
    def decimal_to_float(obj):
        if isinstance(obj, Decimal):
            return float(obj)
        raise TypeError
    
    # Imprimir los resultados de forma legible
    print("\n=== Contenido de la tabla DynamoDB ===")
    for item in response['Items']:
        print("\nItem:")
        print(json.dumps(item, indent=2, ensure_ascii=False, default=decimal_to_float))

if __name__ == '__main__':
    scan_table() 