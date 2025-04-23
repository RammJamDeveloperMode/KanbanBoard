# Kanban Board Assessment

### Description
This project implements a Trello/Kanban-like interface with drag & drop functionality for cards between columns. It includes basic operations for creating, deleting, and updating cards.

### Project Requirements

#### Technology Stack
- **Frontend**: 
  - React with Hooks
  - Tailwind CSS
  - Apollo Client GraphQL (no Redux)
- **Backend**: 
  - Python
  - Graphene (GraphQL)
- **Database**: 
  - DynamoDB Local (for development)
  - AWS DynamoDB (for production)

### Implemented Features
- Kanban interface implemented from scratch
- Drag & drop functionality using `@hello-pangea/dnd`
- CRUD operations for cards:
  - Create new cards
  - Delete cards with confirmation
  - Update cards (title and description)
- Column management:
  - Create new columns
  - Delete columns with confirmation
  - Reorder columns through drag & drop
- Name editing:
  - Edit board name
  - Edit column names
- Automatic initialization:
  - Automatic creation of a default board when starting the application
  - Predefined columns: "To Do", "In Progress", "Completed"

## Project Structure
```
.
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Board.jsx
│   │   │   ├── Column.jsx
│   │   │   ├── Card.jsx
│   │   │   └── AddCardForm.jsx
│   │   └── graphql/
│   │       └── queries.js
│   └── package.json
├── backend/
│   ├── kanban_backend/
│   │   ├── schema.py
│   │   └── settings.py
│   └── requirements.txt
├── Dockerfile.frontend
├── Dockerfile.backend
├── docker-compose.yml
├── nginx.conf
└── .env
```

## Environment Setup

### Prerequisites
- Docker
- Docker Compose
- Node.js (for local development)
- Python 3.9+ (for local development)

# Django Settings
DJANGO_SECRET_KEY=your_secret_key
DEBUG=True

# Frontend Settings
REACT_APP_API_URL=http://localhost:8000/graphql
```

## Running with Docker

1. Build the images:
```bash
docker-compose build
```

2. Start the containers:
```bash
docker-compose up
```

3. Access the application:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- DynamoDB Local: http://localhost:8001

## Local Development

### Frontend
```bash
cd frontend
npm install
npm start
```

### Backend
```bash
cd backend
python -m venv KB
source KB/bin/activate
pip install -r requirements.txt
python manage.py runserver
```

## Technical Features

### Frontend
- Implemented with React and Hooks
- Styled with Tailwind CSS
- Backend communication through Apollo Client
- Drag & drop implemented with `@hello-pangea/dnd`
- State management with React Context and Apollo Cache

### Backend
- GraphQL API with Graphene
- DynamoDB integration (no SQLite)
- Error handling and validations
- Detailed logging

### Docker
- Separate containers for frontend, backend, and DynamoDB
- Nginx as reverse proxy
- Volumes for DynamoDB data persistence
- Implemented healthchecks

### Data Persistence
- **Local Configuration**:
  - Data stored in DynamoDB Local
  - Persistence through Docker volume (`dynamodb-data`)
  - Automatic backup system in `backups/` directory
  - Data management scripts:
    ```bash
    # View current database content
    python scripts/check_dynamodb.py

    # Create data backup
    python scripts/backup_dynamodb.py

    # Restore from backup (interactive)
    python scripts/restore_dynamodb.py
    ```
  - Data persists even after Docker container restarts
  - The restoration script includes:
    - List of available backups
    - Confirmation before restoration
    - Detailed restoration summary
    - Safe error handling

## Implementation Notes
- The Kanban interface was implemented from scratch
- `@hello-pangea/dnd` was used only for drag & drop functionality
- No pre-made Kanban board packages were used
- The technology stack reflects the production stack
- Exclusively DynamoDB database (no SQLite)

----------------------------------------------------------------------------------------------------------------------------


## Descripción
Este proyecto implementa una interfaz tipo Trello/Kanban con funcionalidad de arrastrar y soltar (drag & drop) para tarjetas entre columnas. Incluye operaciones básicas de crear, eliminar y actualizar tarjetas.

## Requisitos del Proyecto

### Stack Tecnológico
- **Frontend**: 
  - React con Hooks
  - Tailwind CSS
  - Apollo Client GraphQL (sin Redux)
- **Backend**: 
  - Python
  - Graphene (GraphQL)
- **Base de Datos**: 
  - DynamoDB Local (para desarrollo)
  - DynamoDB AWS (para producción)

### Características Implementadas
- Interfaz Kanban implementada desde cero
- Funcionalidad de drag & drop usando `@hello-pangea/dnd`
- Operaciones CRUD para tarjetas:
  - Crear nuevas tarjetas
  - Eliminar tarjetas con confirmación
  - Actualizar tarjetas (título y descripción)
- Gestión de columnas:
  - Crear nuevas columnas
  - Eliminar columnas con confirmación
  - Reordenar columnas mediante drag & drop
- Edición de nombres:
  - Editar nombre del tablero
  - Editar nombres de columnas
- Inicialización automática:
  - Creación automática de un tablero por defecto al iniciar la aplicación
  - Columnas predefinidas: "Por Hacer", "En Progreso", "Completado"

## Estructura del Proyecto
```
.
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Board.jsx
│   │   │   ├── Column.jsx
│   │   │   ├── Card.jsx
│   │   │   └── AddCardForm.jsx
│   │   └── graphql/
│   │       └── queries.js
│   └── package.json
├── backend/
│   ├── kanban_backend/
│   │   ├── schema.py
│   │   └── settings.py
│   └── requirements.txt
├── Dockerfile.frontend
├── Dockerfile.backend
├── docker-compose.yml
├── nginx.conf
└── .env
```

## Configuración del Entorno

### Requisitos Previos
- Docker
- Docker Compose
- Node.js (para desarrollo local)
- Python 3.9+ (para desarrollo local)

# Django Settings
DJANGO_SECRET_KEY=your_secret_key
DEBUG=True

# Frontend Settings
REACT_APP_API_URL=http://localhost:8000/graphql
```

## Ejecución con Docker

1. Construir las imágenes:
```bash
docker-compose build
```

2. Iniciar los contenedores:
```bash
docker-compose up
```

3. Acceder a la aplicación:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- DynamoDB Local: http://localhost:8001

## Desarrollo Local

### Frontend
```bash
cd frontend
npm install
npm start
```

### Backend
```bash
cd backend
python -m venv KB
source KB/bin/activate
pip install -r requirements.txt
python manage.py runserver
```

## Características Técnicas

### Frontend
- Implementado con React y Hooks
- Estilizado con Tailwind CSS
- Comunicación con backend mediante Apollo Client
- Drag & drop implementado con `@hello-pangea/dnd`
- Estado gestionado con React Context y Apollo Cache

### Backend
- API GraphQL con Graphene
- Integración con DynamoDB (sin SQLite)
- Manejo de errores y validaciones
- Logging detallado

### Docker
- Contenedores separados para frontend, backend y DynamoDB
- Nginx como proxy inverso
- Volúmenes para persistencia de datos de DynamoDB
- Healthchecks implementados

### Persistencia de Datos
- **Configuración Local**:
  - Datos almacenados en DynamoDB Local
  - Persistencia mediante volumen Docker (`dynamodb-data`)
  - Sistema de backup automático en directorio `backups/`
  - Scripts para gestión de datos:
    ```bash
    # Ver contenido actual de la base de datos
    python scripts/check_dynamodb.py

    # Crear backup de los datos
    python scripts/backup_dynamodb.py

    # Restaurar desde backup (interactivo)
    python scripts/restore_dynamodb.py
    ```
  - Los datos se mantienen incluso después de reiniciar los contenedores Docker
  - El script de restauración incluye:
    - Lista de backups disponibles
    - Confirmación antes de restaurar
    - Resumen detallado de la restauración
    - Manejo seguro de errores

## Notas de Implementación
- La interfaz Kanban fue implementada desde cero
- Se utilizó `@hello-pangea/dnd` solo para la funcionalidad de drag & drop
- No se utilizaron paquetes pre-hechos de tablero Kanban
- El stack tecnológico refleja el stack de producción
- Base de datos exclusivamente DynamoDB (sin SQLite)