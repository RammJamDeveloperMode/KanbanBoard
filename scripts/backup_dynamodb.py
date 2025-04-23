import boto3
from botocore.config import Config
import json
from datetime import datetime
import os
from decimal import Decimal

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

def backup_dynamodb():
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
    
    # Crear directorio de backup si no existe
    backup_dir = 'backups'
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    # Generar nombre de archivo con timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f'{backup_dir}/dynamodb_backup_{timestamp}.json'
    
    # Guardar los datos en un archivo JSON usando el encoder personalizado
    with open(backup_file, 'w') as f:
        json.dump(items, f, indent=2, cls=DecimalEncoder)
    
    print(f"\nBackup creado exitosamente en: {backup_file}")
    print(f"Total de elementos respaldados: {len(items)}")

def restore_dynamodb(backup_file):
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
    
    # Leer el archivo de backup
    with open(backup_file, 'r') as f:
        items = json.load(f)
    
    # Restaurar los elementos
    for item in items:
        # Convertir los números float a Decimal para DynamoDB
        for key, value in item.items():
            if isinstance(value, float):
                item[key] = Decimal(str(value))
        table.put_item(Item=item)
    
    print(f"\nRestauración completada desde: {backup_file}")
    print(f"Total de elementos restaurados: {len(items)}")

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--restore':
        if len(sys.argv) > 2:
            restore_dynamodb(sys.argv[2])
        else:
            print("Error: Debes especificar el archivo de backup a restaurar")
            print("Uso: python backup_dynamodb.py --restore <archivo_backup>")
    else:
        backup_dynamodb() 