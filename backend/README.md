# Spotify Data Warehouse API

Backend RESTful API para la extracción, transformación y carga (ETL) de datos de escucha de Spotify hacia un Data Warehouse en PostgreSQL. Desarrollado con FastAPI, SQLAlchemy y Alembic.

## Características Principales

- **Autenticación PKCE**: Implementación completa del flujo OAuth2 con Proof Key for Code Exchange para login seguro con Spotify.
- **Seguridad JWT**: Protección de endpoints mediante tokens JSON Web Tokens firmados.
- **Proceso ETL Automatizado**: Extracción de historial de escucha, transformación de datos y carga en modelo dimensional (Star Schema).
- **Auditoría de Datos**: Registro detallado de cada ejecución ETL en tabla `etl_audit`.
- **Refresh Token Automático**: Manejo transparente de la expiración de tokens de acceso de Spotify.
- **API Documentada**: Documentación interactiva automática generada con Swagger UI.

## Requisitos Previos

- **Python 3.12+**
- **PostgreSQL**: Se recomienda usar Neon.tech para una base de datos en la nube gratuita y escalable.
- **Cuenta de Desarrollador Spotify**: Registra tu app en Spotify Developer Dashboard para obtener Client ID y configurar Redirect URI.

## Instalación y Configuración

Sigue estos pasos para levantar el proyecto en tu entorno local:

### 1. Clonar el Repositorio

```bash
git clone <URL_DE_TU_REPOSITORIO_GITHUB>
cd backend
```

### 2. Entorno Virtual y Dependencias

Se recomienda usar un entorno virtual para aislar las dependencias:

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate
# En macOS/Linux:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 3. Configuración de Variables de Entorno
El proyecto utiliza variables de entorno para gestionar configuraciones sensibles.
Copia el archivo de ejemplo:

```bash
cp .env.example .env
```

Edita el archivo .env con tus credenciales reales:
- DATABASE_URL: Obtenida desde tu panel de control de Neon.tech. Asegúrate de que incluya ?sslmode=require.
- SPOTIFY_CLIENT_ID: Tu Client ID del dashboard de Spotify.
- SPOTIFY_REDIRECT_URI: Debe coincidir exactamente con la configurada en Spotify (ej. http://127.0.0.1:8000/v1/auth/callback).
- SECRET_KEY: Una cadena aleatoria larga y segura para firmar los JWTs.

### 4. Migraciones de Base de Datos
Aplica las migraciones de Alembic para crear el schema dwh y todas las tablas necesarias (dim_users, dim_artists, dim_tracks, fact_listening_history, etl_audit):

```bash
python -m alembic upgrade head
```

## Ejecución del Servidor
Levanta el servidor de desarrollo con recarga automática:

```bash
uvicorn app.main:app --reload
```

La API estará disponible en:
- Base URL: http://127.0.0.1:8000
- Documentación Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## Estructura del Proyecto
```
backend/
├── app/
│   ├── core/              # Configuración central, seguridad y utilidades
│   │   ├── config.py      # Gestión de variables de entorno con Pydantic Settings
│   │   ├── security.py    # Decodificación de JWT y dependencia de usuario actual
│   │   └── pkce_store.py  # Almacén temporal de sesiones PKCE (desarrollo)
│   ├── v1/                # Versión 1 de la API
│   │   ├── api.py         # Router principal que agrupa todos los módulos
│   │   └── routers/       # Endpoints específicos por dominio
│   │       ├── auth.py    # Login PKCE y Callback
│   │       ├── profile.py # Datos del usuario autenticado
│   │       ├── artists.py # Artistas top desde Spotify
│   │       ├── tracks.py  # Historial reciente desde Spotify
│   │       ├── history.py # Consultas analíticas al DWH
│   │       └── etl.py     # Trigger del proceso ETL
│   ├── services/          # Lógica de negocio y servicios externos
│   │   ├── auth_service.py   # Intercambio de tokens y gestión de usuarios
│   │   ├── spotify_service.py# Cliente HTTP para API de Spotify
│   │   └── etl_service.py    # Lógica de extracción, transformación y carga
│   ├── models.py          # Definición de modelos SQLAlchemy (Tablas DWH)
│   ├── database.py        # Configuración de conexión a PostgreSQL
│   └── main.py            # Punto de entrada de la aplicación FastAPI
├── alembic/               # Scripts de migración de base de datos
├── .env                   # Variables de entorno locales (NO SUBIR A GIT)
├── .env.example           # Plantilla de variables de entorno
├── requirements.txt       # Listado de dependencias Python
└── README.md              # Este archivo
```

## Flujo de Uso Básico
Sigue estos pasos para probar la API completa:

### 1. Autenticación con Spotify
- Ve a http://127.0.0.1:8000/docs
- Busca el endpoint GET /v1/auth/login y haz clic en "Try it out" -> "Execute"
- Serás redirigido a Spotify para autorizar la app "My Spotify Wrapped"
- Al aceptar, serás redirigido a /v1/auth/callback donde verás un JSON como este:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_id": 1,
  "spotify_id": "31zukaxpp6sw3huchk6jrxs6ccye"
}
```

Copia el valor de "access_token" — ese es tu JWT.

### 2. Acceder a Endpoints Protegidos
- En Swagger UI, haz clic en el botón "Authorize" (arriba a la derecha)
- Pega tu JWT (sin la palabra Bearer) en el campo "Value"
- Haz clic en [Authorize] y cierra la ventana
- Ahora puedes ejecutar endpoints protegidos como:
  - GET /v1/profile/me -> Datos del usuario
  - GET /v1/artists/top -> Artistas más escuchados
  - GET /v1/tracks/recent -> Canciones recientes

### 3. Ejecutar el Proceso ETL
- Busca el endpoint POST /v1/etl/run
- Asegúrate de estar autorizado (JWT cargado)
- Haz clic en "Execute"
- Recibirás un resumen como este:

```json
{
  "status": "success",
  "records_processed": 50,
  "artists_new": 15,
  "tracks_new": 47,
  "history_new": 50
}
```

Esto significa que tus datos fueron cargados correctamente en el Data Warehouse.

### 4. Consultar Estadísticas del DWH
- Ejecuta GET /v1/history/stats
- Verás un resumen de cuántas canciones has escuchado por día de la semana:

```json
{
  "user_id": 1,
  "total_listens": 50,
  "by_day_of_week": [
    { "day_of_week": "Monday", "listen_count": 8 },
    { "day_of_week": "Tuesday", "listen_count": 12 }
  ]
}
```

¡Tu Data Warehouse está funcionando!

## Tecnologías Utilizadas
- Framework: FastAPI
- Servidor: Uvicorn
- Base de Datos: PostgreSQL (Neon)
- ORM: SQLAlchemy 2.0
- Migraciones: Alembic
- Validación: Pydantic y Pydantic Settings
- HTTP Client: HTTPX
- Auth: Python-Jose (JWT), OAuth2 PKCE

## Autor
Santiago Capacho  
Proyecto académico - Data Warehouse II - 2026