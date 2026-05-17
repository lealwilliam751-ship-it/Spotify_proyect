# 03. Implementacion del Frontend

## Que se configuro / implemento
1. **Framework React + Vite**: Se utilizo Vite para un desarrollo ultra rapido y un empaquetado optimizado en produccion, configurando el servidor de desarrollo para ejecutarse estrictamente en el puerto 3000.
2. **Punto de Entrada index.html**: Se agrego el punto de entrada HTML index.html ausente en la raiz del frontend, permitiendo la correcta inicializacion del arbol de componentes de React.
3. **Diseno Premium (CSS3 Moderno)**: Se aplico una estetica oscura inspirada en Spotify con una paleta de colores negra y dorada, efectos de Glassmorphism, degradados suaves, fuentes premium (Cinzel y Rajdhani) y micro-animaciones fluidas.
4. **Dashboard Dinamico**: Incluye cuatro widgets de resumen en tiempo real:
   - Artistas Top (dim_artists)
   - Canciones Top (dim_tracks)
   - Total de Reproducciones (fact_listening_history)
   - Genero Principal (calculado dinamicamente)
5. **Control de Estado Vacio**: Se implemento un control de renderizado inteligente que detecta si el Data Warehouse esta vacio, mostrando una interfaz limpia que guia al usuario a ejecutar su primera carga ETL en lugar de mostrar pantallas en blanco.
6. **Vista de Perfil de Usuario**: Se anadio una pantalla completa de perfil con un avatar personalizado y todos los metadatos del usuario logueado en Spotify.
7. **Control del ETL**: Interfaz interactiva de tipo Stepper que muestra el progreso del pipeline y permite gatillar la sincronizacion manual, mostrando una tabla de auditoria en tiempo real (etl_audit).

## Screenshots
![Dashboard UI](assets/dashboard_ui.png)
![ETL Status UI](assets/etl_status_ui.png)

## Prompt utilizado
"Crea un dashboard premium usando React y Vite. El diseno debe ser oscuro con una paleta negra y dorada, con una barra lateral y tarjetas tipo glassmorphism. Incluye una pagina para el perfil del usuario, widgets interactivos para estadisticas clave y una seccion para el pipeline ETL que muestre un stepper interactivo del proceso y el historial de auditoria."

## Tecnica de prompting aplicada
**Role Prompting**: "Actua como un disenador UI/UX experto en aplicaciones musicales modernas. Disena una interfaz que se sienta viva y profesional con micro-animaciones en CSS, degradados elegantes y una paleta dorada premium..."
