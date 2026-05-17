# 04. Pipeline ETL (Extract, Transform, Load)

## Qué se configuró / implementó
1. **Fases del ETL**: Se implementaron funciones específicas para cada fase:
    - **Extract**: Consultas a los 4 endpoints de Spotify usando `SpotifyClient`.
    - **Transform**: Mapeo de objetos JSON de Spotify a modelos de SQLAlchemy, incluyendo la limpieza de datos y normalización de fechas.
    - **Load**: Inserción en las tablas `dim_users`, `dim_artists`, `dim_tracks` y `fact_listening_history` usando la cláusula `ON CONFLICT DO NOTHING` para garantizar la idempotencia.
2. **Carga Incremental**: Se implementó el cursor basado en `cursor_next_ms` de la tabla `etl_audit`, permitiendo que cada ejecución solo traiga canciones reproducidas después de la última sincronización.
3. **Auditoría**: Cada ejecución registra automáticamente su duración, estado (RUNNING, COMPLETED, FAILED) y el conteo de nuevos registros insertados por cada tabla.

## Screenshots
![Tabla Auditoría](assets/etl_audit_table.png)

## Prompt utilizado
"Crea un servicio ETL que realice la extracción de los 4 endpoints requeridos. La carga al historial de escucha debe ser incremental, leyendo el último cursor de la tabla etl_audit. Asegúrate de que los artistas y canciones se creen en sus dimensiones si no existen antes de insertar en la tabla de hechos."

## Técnica de prompting aplicada
**Few-Shot Prompting**: Se le proporcionaron ejemplos de cómo manejar las claves foráneas en SQLAlchemy para asegurar que la IA entendiera la jerarquía de inserción (primero dimensiones, luego hechos).
