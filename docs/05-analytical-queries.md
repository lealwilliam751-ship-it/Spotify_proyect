# 05. Consultas Analiticas y Resultados

Este documento detalla las consultas SQL analiticas ejecutadas directamente sobre el Data Warehouse en Neon PostgreSQL. Estas consultas validan el correcto funcionamiento del Star Schema (Galaxy Schema) y demuestran la capacidad de extraer insights del historial de escucha.

## Consulta 1: Top 10 Artistas Mas Escuchados

Esta consulta calcula los 10 artistas con mayor numero de reproducciones registradas en el historial de escucha del usuario. Realiza un JOIN entre la tabla de hechos y la dimension de artistas.

```sql
SELECT 
    a.name AS artista,
    COUNT(T1.id) AS total_reproducciones
FROM 
    dwh.fact_listening_history T1
JOIN 
    dwh.dim_artists a ON T1.artist_id = a.artist_id
GROUP BY 
    a.name
ORDER BY 
    total_reproducciones DESC
LIMIT 10;
```

### Interpretacion de Resultados
Permite identificar las preferencias musicales absolutas del usuario en el DWH. Ayuda a alimentar el primer widget de visualizacion en el dashboard.

---

## Consulta 2: Actividad de Escucha por Hora del Dia

Esta consulta agrupa el historial de escucha por la hora del dia (campo extraido y normalizado durante la fase de transformacion en `hour_of_day`) para identificar los picos de consumo musical del usuario.

```sql
SELECT 
    T1.hour_of_day AS hora,
    COUNT(T1.id) AS cantidad_reproducciones
FROM 
    dwh.fact_listening_history T1
GROUP BY 
    T1.hour_of_day
ORDER BY 
    hora ASC;
```

### Interpretacion de Resultados
Permite trazar los habitos cotidianos del usuario (por ejemplo, si escucha mas musica en horario laboral/estudio, por la noche, o al transportarse). Los resultados alimentan directamente el grafico de areas del frontend.

---

## Consulta 3: Actividad de Escucha por Dia de la Semana

Agrupa las reproducciones de la tabla de hechos por el dia de la semana (campo normalizado en `day_of_week`) para observar la variacion de reproducciones entre dias laborales y fines de semana.

```sql
SELECT 
    T1.day_of_week AS dia_semana,
    COUNT(T1.id) AS cantidad_reproducciones
FROM 
    dwh.fact_listening_history T1
GROUP BY 
    T1.day_of_week
ORDER BY 
    CASE T1.day_of_week
        WHEN 'Monday' THEN 1
        WHEN 'Tuesday' THEN 2
        WHEN 'Wednesday' THEN 3
        WHEN 'Thursday' THEN 4
        WHEN 'Friday' THEN 5
        WHEN 'Saturday' THEN 6
        WHEN 'Sunday' THEN 7
    END;
```

### Interpretacion de Resultados
Permite contrastar la actividad recreativa de fin de semana contra el comportamiento diario regular del usuario. Alimenta el grafico de barras del dashboard.

---

## Consulta 4: Analisis de Popularidad Promedio por Cancion

Clasifica las canciones escuchadas por el usuario segun su nivel de popularidad (mainstream, emerging, underground) mediante un analisis estadistico de agregacion sobre la dimension `dim_tracks`.

```sql
SELECT 
    CASE 
        WHEN t.popularity >= 80 THEN 'Viral / Mainstream Top'
        WHEN t.popularity BETWEEN 50 AND 79 THEN 'Emerging / Popular'
        ELSE 'Underground / Alternativo'
    END AS categoria_popularidad,
    COUNT(DISTINCT T1.track_id) AS canciones_unicas,
    COUNT(T1.id) AS reproducciones_totales
FROM 
    dwh.fact_listening_history T1
JOIN 
    dwh.dim_tracks t ON T1.track_id = t.track_id
GROUP BY 
    categoria_popularidad
ORDER BY 
    reproducciones_totales DESC;
```

### Interpretacion de Resultados
Determina si el usuario consume principalmente musica comercial de alta difusion o si su perfil se inclina hacia artistas emergentes e independientes.

---

## Consulta 5: Auditoria de Cargas ETL

Consulta el historial de auditoria en `etl_audit` para validar el volumen de insercion incremental de datos y la duracion de cada proceso.

```sql
SELECT 
    audit_id,
    started_at,
    finished_at,
    (duration_ms / 1000.0) AS duracion_segundos,
    status,
    artists_new,
    tracks_new,
    history_new
FROM 
    dwh.etl_audit
ORDER BY 
    started_at DESC;
```

### Interpretacion de Resultados
Garantiza el control de calidad sobre la ejecucion del pipeline, registrando las nuevas filas insertadas de forma incremental en cada fase.

## Screenshots
![Resultados Consultas Analiticas](assets/analytical_queries_results.png)

## Prompt utilizado
"Genera las 5 consultas analiticas SQL en base al Galaxy Schema del DWH de Spotify para obtener el top de artistas, actividad por hora, actividad por dia, popularidad de canciones y auditoria de cargas ETL, incluyendo la interpretacion de cada resultado."

## Tecnica de prompting aplicada
**Chain-of-Thought**: Se estructuro paso a paso cada consulta analitica partiendo del modelo dimensional, asegurando los JOINs correctos entre la tabla de hechos y las dimensiones.
