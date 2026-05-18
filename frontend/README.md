# Spotify Data Warehouse Frontend

Cliente web interactivo y premium para la visualización de datos personales de escucha de Spotify y la orquestación del pipeline ETL hacia el Data Warehouse. Desarrollado con React, Vite, Recharts y Lucide React.

## Características Principales

- **Diseño Premium**: Estética oscura inspirada en Spotify con una paleta de colores negra y dorada, efectos de Glassmorphism, degradados suaves y micro-animaciones fluidas.
- **Dashboard Dinámico en Tiempo Real**: 
  - Visualización del Top 5 Artistas y Top 5 Canciones más escuchados almacenados en el DWH.
  - Indicadores numéricos de resumen con efecto de conteo progresivo animado (Count-Up).
- **Gráficos Interactivos**:
  - Gráfico de áreas para el análisis de Actividad por Hora a lo largo del día.
  - Gráfico de barras para el análisis de Actividad por Día de la Semana.
  - Barras animadas de proporción para tus Géneros Favoritos.
- **Control y Orquestación del ETL**: Interfaz interactiva de tipo Stepper (Extract -> Transform -> Load) que muestra el estado de ejecución en tiempo real y permite disparar la sincronización de datos manualmente.
- **Historial de Auditoría**: Tabla completa de auditoría de ejecuciones pasadas (etl_audit) con colores de estado dinámicos (COMPLETED, FAILED, RUNNING).
- **Autenticación Integrada**: Captura transparente del JWT del backend para gestionar sesiones activas y redirigir automáticamente en caso de expiración (error 401).

## Requisitos Previos

- **Node.js 18.0+**
- **npm** (incluido con Node.js)
- **Servidor Backend Activo**: El frontend depende de la API RESTful del backend en ejecución (por defecto en http://127.0.0.1:8080 o según tu configuración).

## Instalación y Configuración

Sigue estos pasos para levantar el frontend en tu entorno local:

### 1. Navegar al Directorio del Frontend

```bash
cd frontend
```

### 2. Instalar Dependencias

```bash
npm install
```

### 3. Configuración de Variables de Entorno

El cliente consume los servicios del backend a través de la URL base configurada en src/api.js. Por defecto, está configurado para comunicarse con:
http://127.0.0.1:8080 (o http://localhost:8080).

Si tu API corre en un puerto o dirección distinta, edita la constante API_BASE_URL en src/api.js:
```javascript
const API_BASE_URL = "http://127.0.0.1:8080";
```

## Ejecución del Servidor de Desarrollo

Levanta el entorno de desarrollo local con recarga en caliente:

```bash
npm run dev
```

El cliente web estará disponible en:
- **URL**: http://localhost:3000 (puerto configurado en vite.config.js).

Para realizar una compilación optimizada para producción:
```bash
npm run build
```
Esto generará los archivos estáticos listos para despliegue en la carpeta dist/.

## Estructura del Proyecto

```
frontend/
├── dist/                  # Distribución generada para producción (tras build)
├── node_modules/          # Módulos y dependencias de Node.js
├── src/                   # Código fuente principal de la aplicación
│   ├── assets/            # Imágenes estáticas y logotipos (.svg, .png)
│   ├── api.js             # Mapeo y llamadas a los endpoints de la API del backend
│   ├── App.css            # Estilos CSS específicos de la app
│   ├── App.jsx            # Componente raíz con el Dashboard, Login y Orquestación ETL
│   ├── index.css          # Estilos globales y variables de diseño premium (CSS Variables)
│   └── main.jsx           # Punto de entrada de inicialización de React 18
├── .gitignore             # Exclusión de archivos para control de versiones
├── index.html             # Estructura del documento HTML base (Vite Entrypoint)
├── package.json           # Manifiesto del proyecto y listado de dependencias
├── vite.config.js         # Configuración del entorno de Vite y servidor (Puerto 3000)
└── README.md              # Este archivo descriptivo
```

## Flujo de Uso Básico

1. **Pantalla de Inicio**: Al ingresar, verás la página de bienvenida donde podrás hacer clic en Conectar con Spotify.
2. **Autorización**: Serás redirigido de manera segura a la página oficial de Spotify para autorizar el acceso a tus datos de escucha.
3. **Inicio de Sesión**: Spotify te devolverá al backend, el cual generará un JWT y te redirigirá automáticamente de vuelta al frontend (http://localhost:3000/?access_token=...). El frontend guardará tu sesión en localStorage.
4. **Dashboard Principal**: Verás instantáneamente tus métricas del Data Warehouse: reproducciones totales, tus 5 artistas y canciones preferidas y los gráficos interactivos de tus horarios y días de mayor actividad.
5. **Panel ETL**: Ve a la pestaña Pipeline ETL en la barra lateral para ver el stepper animado. Haz clic en Ejecutar Pipeline para sincronizar tus últimas reproducciones y observa cómo se actualiza la tabla de auditoría en la parte inferior.

## Tecnologías Utilizadas

- **Framework**: React 18 (Vite JS)
- **Visualización de Datos**: Recharts (Gráficos interactivos de Áreas y Barras)
- **Diseño**: CSS3 moderno con variables dinámicas, animaciones CSS avanzadas y efecto Glassmorphism
- **Iconografía**: Lucide React
- **Autenticación**: Integración segura con OAuth 2.0 PKCE a través de JWT en LocalStorage

## Autor

William Leal
Proyecto académico - Data Warehouse II - 2026
