#!/bin/bash

# Crear directorio para DynamoDB
mkdir -p dynamodb_local
cd dynamodb_local

# Descargar DynamoDB Local
curl -L https://s3.us-west-2.amazonaws.com/dynamodb-local/dynamodb_local_latest.tar.gz -o dynamodb_local_latest.tar.gz

# Extraer el archivo
tar -xzf dynamodb_local_latest.tar.gz

# Iniciar DynamoDB Local
java -Djava.library.path=./DynamoDBLocal_lib -jar DynamoDBLocal.jar -sharedDb -port 8002 &

echo "DynamoDB Local iniciado en http://localhost:8002" 