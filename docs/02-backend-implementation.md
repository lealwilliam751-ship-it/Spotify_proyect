# 02. Implementación del Backend

## Qué se configuró / implementó
1. **Autenticación PKCE**: Se implementó el flujo completo de "Authorization Code Flow with PKCE" en el servicio `SpotifyService` y el router `auth.py`. Esto permite una autenticación segura sin necesidad de exponer el `client_secret` en el frontend.
2. **Seguridad JWT**: Se configuró un sistema de tokens JWT para proteger los endpoints del DWH, asegurando que solo el usuario dueño de los datos pueda consultarlos.
3. **Estructura de Servicios**: Se crearon capas de servicios (`spotify_service`, `etl_service`) para separar la lógica de la API de Spotify de la lógica de persistencia en la base de datos.
4. **Endpoints de Consulta**: Se habilitaron rutas para obtener el perfil, artistas top, canciones top e historial de escucha directamente desde el esquema `dwh`.

## Screenshots
![Swagger Backend](assets/swagger_backend.png)

## Prompt utilizado
"Implementa el flujo de autenticación OAuth PKCE de Spotify en FastAPI. Crea un servicio dedicado para manejar la generación de code_verifier y code_challenge, y un router que maneje los endpoints de /login y /callback, guardando los tokens en la tabla dim_users y emitiendo un JWT propio de la app."

## Técnica de prompting aplicada
**Chain-of-Thought**: Se guió a la IA para que primero definiera la lógica criptográfica de PKCE, luego la persistencia en la base de datos y finalmente la integración con los routers de FastAPI.
