# Arquitectura del Sistema Admin Kiosk 3

## Visión General
Sistema de gestión de kioscos interactivos basado en microservicios, diseñado para alta disponibilidad y escalabilidad.

## Microservicios
1. Auth Service (Puerto 5001)
2. Kiosk Service (Puerto 5002)
3. Payment Service (Puerto 5003)
4. AI Service (Puerto 5004)
5. WebSocket Service (Puerto 5005)
6. Notification Service (Puerto 5006)

## Tecnologías
- Backend: Python/Flask
- Base de datos: PostgreSQL
- Cache: Redis
- Mensajería: WebSockets
- Contenedores: Docker/Kubernetes 