# Respuestas Tecnicas - William

Este documento contiene las respuestas individuales a las preguntas planteadas en la Seccion 5 del Examen Final de Bases de Datos II, explicadas de forma sencilla, clara y directa.

---

## Pregunta 1
**¿Cual es la granularidad de `fact_listening_history`? ¿Que representa exactamente una fila? ¿Por que `played_at` no puede ser clave primaria por si sola y como se resolvio eso en el modelo?**

### Respuesta:
La granularidad de la tabla `fact_listening_history` es a nivel de reproduccion individual por usuario. En palabras sencillas, esto significa que cada fila representa una sola cancion escuchada por una persona en un momento especifico. Cada vez que alguien termina de reproducir un tema, se crea una fila para registrar ese evento.

El campo `played_at` guarda la fecha y hora exacta en la que termino la cancion. Este campo no puede ser la clave primaria por si solo debido a dos problemas principales:
1. **Multiples usuarios:** Como el Data Warehouse esta disenado para soportar mas de un usuario, si dos personas distintas terminan de escuchar cualquier cancion exactamente en el mismo segundo, habria un choque de claves duplicadas en la base de datos.
2. **Duplicados de la API:** En ocasiones extremas, la API de Spotify podria reportar dos marcas de tiempo identicas para un mismo usuario debido a problemas de red o reintentos de conexion del telefono o computadora.

Para solucionar esto en el modelo, decidimos definir una clave primaria compuesta natural usando `(user_id, played_at)`. Asi garantizamos que cada evento de escucha sea unico para cada usuario, sin importar si coincide el segundo exacto con otra persona. Adicionalmente, el motor de la base de datos genera un identificador incremental `id` para que sea mas facil relacionar las tablas en las consultas del ORM.

---

## Pregunta 2
**El ETL usa `ON CONFLICT (spotify_id) DO NOTHING` en las dimensiones y `ON CONFLICT (user_id, played_at) DO NOTHING` en la tabla de hechos. ¿Que propiedad garantiza eso? ¿Que pasaria si no existiera esa clausula y corrieran el ETL dos veces el mismo dia?**

### Respuesta:
La propiedad que nos garantiza esto se llama **Idempotencia**. Basicamente, significa que si ejecutamos la misma operacion (correr el ETL) una o cien veces, el resultado en la base de datos va a ser exactamente el mismo que si la hubieramos corrido una sola vez. No se duplica informacion ni se rompe el sistema.

Si no tuviéramos esta clausula de `ON CONFLICT DO NOTHING` pasarian dos cosas graves:
1. Al correr el ETL por segunda vez en el mismo dia, la base de datos intentaria insertar canciones o artistas que ya existen. Como tenemos restricciones de unicidad, el sistema lanzaria de inmediato un error en la consola (`UniqueViolation` o `IntegrityError`) y abortaria todo el proceso de carga de datos.
2. Si no tuviéramos restricciones de unicidad en las tablas ni la clausula `ON CONFLICT`, las mismas canciones y artistas se volverian a meter una y otra vez en cada ejecucion. Esto duplicaria (o triplicaria) falsamente el total de reproducciones y arruinaria por completo los graficos y metricas del dashboard, mostrando informacion irreal.

---

## Pregunta 3
**`dim_tracks` tiene una FK hacia `dim_artists`. ¿Que tipo de schema genera esa relacion entre dimensiones? ¿Cual seria la alternativa en un star schema puro? ¿Por que se decidio mantener la FK y cual es el trade-off?**

### Respuesta:
Al conectar la dimension `dim_tracks` directamente con `dim_artists`, rompemos la regla clasica de independencia entre dimensiones que exige un Star Schema puro. Esto convierte a nuestro diseno en un modelo **Galaxy Schema** (o un hibrido con **Snowflake Schema** debido a la relacion directa entre dimensiones).

En un **Star Schema puro**, la alternativa habria sido **desnormalizar por completo** la dimension de canciones. Esto significa que tendriamos que quitar la relacion FK hacia la tabla de artistas y meter toda la informacion del artista (como el nombre, los seguidores, la popularidad y sus generos musicales) directamente dentro de la tabla `dim_tracks` como columnas adicionales.

### ¿Por que se decidio mantener la FK y cual es el trade-off?
Decidimos mantener la relacion directa (FK) por orden y consistencia de los datos. En Spotify, los artistas tienen datos cambiantes (como los seguidores y la popularidad) y generos musicales guardados en listas. Si metemos toda esa informacion repetida por cada cancion, duplicariamos demasiado texto y harian muy lentas las actualizaciones.

El **trade-off** (la balanza de ventajas y desventajas) es:
- **La desventaja:** Ahora las consultas analiticas complejas necesitan hacer un `JOIN` extra (ir de la tabla de hechos a tracks, y de tracks a artistas) para poder cruzar los datos de reproduccion con los nombres y generos del artista, lo que puede tomar un poco mas de procesamiento en bases de datos gigantescas.
- **La ventaja:** Ahorramos mucho espacio en disco, mantenemos los datos limpios y organizados sin duplicidad, y si la popularidad de un artista cambia, solo la actualizamos en una sola fila dentro de `dim_artists` en lugar de cambiar cientos de filas en `dim_tracks`.

---

## Pregunta 4
**Expliquen el flujo completo desde que el usuario hace clic en "Conectar con Spotify" hasta que el frontend tiene el JWT en `localStorage`. ¿Que es PKCE y por que se usa?**

### Respuesta:
### Flujo Completo paso a paso:
1. El usuario entra a la web y presiona el boton "Conectar con Spotify".
2. El frontend lo envia al backend al endpoint `/v1/auth/login`.
3. El backend redirige de inmediato al usuario a la pagina de autorizacion oficial de Spotify con el ID de cliente, los permisos que necesitamos (scope) y una URL para regresar (redirect_uri).
4. El usuario inicia sesion en Spotify (si no la tenia abierta) y acepta compartir su informacion con nuestra aplicacion.
5. Spotify redirige al usuario de vuelta a nuestro backend, trayendo en la URL un codigo temporal de autorizacion de un solo uso (`code`).
6. Nuestro backend toma ese codigo y hace una peticion interna y segura a los servidores de Spotify para cambiarlo por los tokens reales (`Access Token` y `Refresh Token`).
7. El backend consulta el perfil del usuario en Spotify, lo guarda en la dimension `dim_users` para registrarlo, y genera un token JWT firmado propio de nuestra aplicacion para manejar la sesion local.
8. El backend redirige al navegador de vuelta al frontend a la pagina de callback, metiendo el token JWT en los parametros de la URL (`/callback?access_token=JWT`).
9. El frontend recibe ese JWT en el callback, lo guarda de forma segura en el `localStorage` (como `spotify_dwh_token`), limpia la URL del navegador usando Javascript para que no se vea el token en la barra de direcciones, y abre el dashboard principal de la app.

### ¿Que es PKCE y por que se usa?
**PKCE** (*Proof Key for Code Exchange*) es una medida de seguridad añadida sobre el flujo OAuth 2.0 tradicional. Se usa especificamente para proteger aplicaciones que corren directamente en el navegador del usuario (como React) donde el codigo fuente es visible y no se puede ocultar de forma segura una clave secreta de cliente.

Funciona creando un "secreto dinamico" al vuelo:
- El frontend genera una clave secreta aleatoria llamada **Code Verifier**.
- Luego la encripta (normalmente con SHA-256) creando un **Code Challenge** y lo envia a Spotify al iniciar el login.
- Cuando el backend o el cliente piden el token definitivo usando el codigo de autorizacion temporal, deben enviar tambien la clave original `Code Verifier` en texto plano. Spotify la encripta y comprueba si coincide con el `Code Challenge` original. Esto asegura que la persona que esta pidiendo los tokens de acceso al final es exactamente la misma persona que inicio el proceso de inicio de sesion, evitando que un atacante intercepte el codigo en el camino.

---

## Pregunta 5
**¿Para que sirve `cursor_next_ms` en `etl_audit`? ¿Que problema resuelve? ¿Que pasaria si escuchan 80 canciones en un día sin correr el ETL?**

### Respuesta:
El campo `cursor_next_ms` en la tabla `etl_audit` sirve como una especie de **marcador o punto de control**. Guarda la fecha y hora en milisegundos de la ultima cancion que logramos procesar y guardar correctamente en la base de datos durante la ejecucion del ETL.

### ¿Que problema resuelve?
Resuelve el problema de la **duplicidad y la lentitud al cargar datos**. Sin este cursor, cada vez que corramos el ETL tendriamos que descargar todas las canciones de Spotify desde cero, procesando cientos de registros que ya tenemos e inundando la base de datos de colisiones y reintentos innecesarios. Gracias al cursor, cuando el ETL vuelve a arrancar, lee cual fue la ultima fecha registrada (`cursor_next_ms`) y le pide a la API de Spotify unicamente las canciones reproducidas *despues* de ese momento exacto (`after = cursor_next_ms`).

### ¿Que pasaria si escuchan 80 canciones en un dia sin correr el ETL?
La API de Spotify tiene una limitacion fisica estricta en su endpoint de canciones escuchadas recientemente (`recently-played`): **solo guarda e informa las ultimas 50 canciones reproducidas**.

Si escuchas 80 canciones en un dia sin ejecutar el ETL:
1. Las 30 canciones mas viejas que escuchaste al principio de ese dia seran desplazadas y eliminadas de la cola de la API por las nuevas canciones que escuchaste despues.
2. Cuando finalmente corras el ETL al final del dia, la API de Spotify solo le entregara al backend las 50 canciones mas recientes.
3. Las 30 canciones mas viejas se **perderan de forma definitiva** y nunca ingresaran al Data Warehouse.

Para solucionar esto en la vida real, el ETL no se corre a mano, sino que se programa con una tarea automatizada (como un cron job) para que se ejecute en segundo plano cada 1 o 2 horas, capturando los datos antes de que se desborde el limite de 50 canciones de Spotify.
