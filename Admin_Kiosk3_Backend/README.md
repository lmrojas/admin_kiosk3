# Admin Kiosk 3 - Sistema de Gestión de Kioskos

## Descripción
Sistema de gestión de kioskos basado en microservicios para administrar ventas, pagos, inventario y análisis de datos.

## Servicios
- Auth Service (Puerto 5001): Autenticación y autorización
- Kiosk Service (Puerto 5002): Gestión de kioskos y ventas
- Payment Service (Puerto 5003): Procesamiento de pagos
- AI Service (Puerto 5004): Análisis predictivo y recomendaciones
- WebSocket Service (Puerto 5005): Comunicación en tiempo real
- Notification Service (Puerto 5006): Sistema de notificaciones

## Requisitos
- Python 3.9+
- PostgreSQL 13+
- Redis 6+
- Docker y Docker Compose

## Instalación
1. Clonar repositorio
2. Copiar .env.example a .env y configurar variables
3. Ejecutar `docker-compose up --build`

## Desarrollo
- Instalar dependencias: `pip install -r requirements.txt`
- Ejecutar tests: `pytest`
- Formatear código: `black .`

## Documentación
Ver documentación detallada en /docs 