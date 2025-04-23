import boto3
from botocore.config import Config
import json
from decimal import Decimal
import os
import sys
from datetime import datetime

def list_backups():
    """Lista todos los backups disponibles"""
    backup_dir = 'backups'
    if not os.path.exists(backup_dir):
        print("No existe el directorio de backups")
        return []
    
    backups = [f for f in os.listdir(backup_dir) if f.startswith('dynamodb_backup_') and f.endswith('.json')]
    backups.sort(reverse=True)  # Ordenar del más reciente al más antiguo
    
    if not backups:
        print("No se encontraron backups")
        return []
    
    print("\nBackups disponibles:")
    for i, backup in enumerate(backups, 1):
        print(f"{i}. {backup}")
    return backups

def restore_backup(backup_file):
    """Restaura un backup específico"""
    try:
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
        
        # Limpiar la tabla actual
        print("\nLimpiando tabla actual...")
        scan = table.scan()
        with table.batch_writer() as batch:
            for item in scan['Items']:
                batch.delete_item(
                    Key={
                        'id': item['id'],
                        'type': item['type']
                    }
                )
        
        # Restaurar los elementos
        print("Restaurando elementos...")
        with table.batch_writer() as batch:
            for item in items:
                # Convertir los números float a Decimal para DynamoDB
                for key, value in item.items():
                    if isinstance(value, float):
                        item[key] = Decimal(str(value))
                batch.put_item(Item=item)
        
        print(f"\nRestauración completada exitosamente desde: {backup_file}")
        print(f"Total de elementos restaurados: {len(items)}")
        
        # Mostrar resumen de lo restaurado
        boards = [item for item in items if item['type'] == 'board']
        columns = [item for item in items if item['type'] == 'column']
        cards = [item for item in items if item['type'] == 'card']
        
        print("\nResumen de la restauración:")
        print(f"- Tableros: {len(boards)}")
        print(f"- Columnas: {len(columns)}")
        print(f"- Tarjetas: {len(cards)}")
        
    except Exception as e:
        print(f"\nError durante la restauración: {str(e)}")
        sys.exit(1)

def main():
    backups = list_backups()
    if not backups:
        return
    
    try:
        choice = input("\nSelecciona el número del backup a restaurar (o 'q' para salir): ")
        if choice.lower() == 'q':
            return
        
        index = int(choice) - 1
        if index < 0 or index >= len(backups):
            print("Selección inválida")
            return
        
        backup_file = os.path.join('backups', backups[index])
        print(f"\nRestaurando backup: {backup_file}")
        
        confirm = input("¿Estás seguro de que quieres restaurar este backup? (s/n): ")
        if confirm.lower() == 's':
            restore_backup(backup_file)
        else:
            print("Restauración cancelada")
    
    except ValueError:
        print("Por favor, ingresa un número válido")
    except KeyboardInterrupt:
        print("\nOperación cancelada por el usuario")

if __name__ == '__main__':
    main() 