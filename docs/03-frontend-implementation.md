# 03. Implementación del Frontend

## Qué se configuró / implementó
1. **Framework Next.js**: Se utilizó el App Router de Next.js para una navegación fluida y optimizada.
2. **Diseño Premium (Tailwind CSS)**: Se aplicó una estética oscura inspirada en Spotify, con efectos de "Glassmorphism" y micro-animaciones.
3. **Dashboard Dinámico**: Widgets que muestran en tiempo real los datos cargados en el DWH (artistas y tracks).
4. **Control del ETL**: Interfaz para disparar la sincronización y monitorear el historial de auditoría con estados visuales (colores por estado).

## Screenshots
![Dashboard UI](assets/dashboard_ui.png)
![ETL Status UI](assets/etl_status_ui.png)

## Prompt utilizado
"Crea un dashboard premium usando Next.js y Tailwind CSS. El diseño debe ser oscuro, con una barra lateral y tarjetas tipo glassmorphism. Incluye una página para el pipeline ETL que muestre una tabla con el historial de auditoría y un botón destacado para sincronizar."

## Técnica de prompting aplicada
**Role Prompting**: "Actúa como un diseñador UI/UX experto en aplicaciones musicales modernas. Diseña una interfaz que se sienta viva y profesional..."
