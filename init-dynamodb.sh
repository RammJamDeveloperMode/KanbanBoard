#!/bin/bash

# Esperar a que DynamoDB esté listo
echo "Esperando a que DynamoDB esté listo..."
while ! curl -s http://localhost:8002/shell/ > /dev/null; do
    sleep 1
done

# Crear la tabla si no existe
echo "Creando tabla kanban_board..."
aws dynamodb create-table \
    --endpoint-url http://localhost:8002 \
    --table-name kanban_board \
    --attribute-definitions \
        AttributeName=id,AttributeType=S \
        AttributeName=type,AttributeType=S \
        AttributeName=column_id,AttributeType=S \
        AttributeName=board_id,AttributeType=S \
    --key-schema \
        AttributeName=id,KeyType=HASH \
    --global-secondary-indexes \
        "[
            {
                \"IndexName\": \"TypeIndex\",
                \"KeySchema\": [{\"AttributeName\":\"type\",\"KeyType\":\"HASH\"}],
                \"Projection\":{\"ProjectionType\":\"ALL\"},
                \"ProvisionedThroughput\":{\"ReadCapacityUnits\":5,\"WriteCapacityUnits\":5}
            },
            {
                \"IndexName\": \"ColumnIdIndex\",
                \"KeySchema\": [
                    {\"AttributeName\":\"column_id\",\"KeyType\":\"HASH\"},
                    {\"AttributeName\":\"type\",\"KeyType\":\"RANGE\"}
                ],
                \"Projection\":{\"ProjectionType\":\"ALL\"},
                \"ProvisionedThroughput\":{\"ReadCapacityUnits\":5,\"WriteCapacityUnits\":5}
            },
            {
                \"IndexName\": \"BoardIdIndex\",
                \"KeySchema\": [
                    {\"AttributeName\":\"board_id\",\"KeyType\":\"HASH\"},
                    {\"AttributeName\":\"type\",\"KeyType\":\"RANGE\"}
                ],
                \"Projection\":{\"ProjectionType\":\"ALL\"},
                \"ProvisionedThroughput\":{\"ReadCapacityUnits\":5,\"WriteCapacityUnits\":5}
            }
        ]" \
    --provisioned-throughput \
        ReadCapacityUnits=5,WriteCapacityUnits=5

echo "Tabla creada exitosamente!" 