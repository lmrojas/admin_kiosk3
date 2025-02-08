# Documentación de Reglas MDC - Admin_Kiosk3

## Índice de Reglas
1. [General](#1-generalmdc)
2. [Modelos](#2-modelsmdc)
3. [Vistas](#3-viewsmdc)
4. [Servicios](#4-servicesmdc)
5. [Middleware](#5-middlewaremdc)
6. [Seguridad](#6-securitymdc)
7. [Logging](#7-logginmdc)
8. [Configuración](#8-configmdc)
9. [Notificaciones](#9-notificationsmdc)
10. [WebSockets](#10-websocketsmdc)
11. [CI/CD](#11-cicdmdc)
12. [IA](#12-aimdc)

## 1. general.mdc
Reglas generales del proyecto: convenciones de nombres, estructura de directorios, dependencias, modularidad y evitar duplicación de código.

### Convenciones de Nombres
- Usar `snake_case` para nombres de archivos y variables
- Usar `UpperCamelCase` para nombres de clases
- Escribir constantes en MAYÚSCULAS
- Seguir las pautas de PEP8

### Estructura de Directorios
- Organizar el proyecto siguiendo el patrón MVT
- Separar carpetas para modelos, vistas, templates y archivos estáticos
- Incluir carpetas adicionales para servicios, middleware y configuración

### Dependencias
- Definir todas las dependencias en `requirements.txt` con versiones fijas
- Utilizar entornos virtuales
- Mantener actualizados los paquetes

### Modularidad
- Dividir la aplicación en módulos desacoplados por funcionalidad
- Cada módulo debe incluir su propia lógica

## 2. models.mdc
Reglas para la capa de modelos (ORM con SQLAlchemy y PostgreSQL).

### Nombres y Definición
- Definir modelos como clases en **PascalCase** (ejemplo: `User`)
- Utilizar `__tablename__` en formato **snake_case** (ejemplo: `users`)

### Atributos y Tipos
- Usar tipos SQLAlchemy adecuados (Integer, String, DateTime, etc.)
- Definir restricciones coherentes (nullable, unique, default)
- Incluir campos estándares (`id`, `created_at`)

### Relaciones
- Usar `relationship` y `ForeignKey` con nombres consistentes
- Configurar lazy loading apropiadamente

### Migraciones
- Usar Alembic/Flask-Migrate para cambios en esquema
- Mantener control de versiones de BD

## 3. views.mdc
Reglas para vistas y controladores usando Blueprints.

### Organización
- Dividir rutas en Blueprints por funcionalidad
- Registrar cada Blueprint con prefijo adecuado

### Responsabilidades
- Limitar vistas a gestión HTTP
- Delegar lógica de negocio a servicios

### Templates
- Usar Jinja2 para plantillas HTML
- Mantener solo lógica de presentación

### API
- Definir rutas RESTful claras
- Usar códigos HTTP apropiados

## 4. services.mdc
Reglas para la capa de servicios y lógica de negocio.

### Desacoplamiento
- Independencia del contexto Flask
- No depender directamente de `request`

### Organización
- Agrupar por dominio funcional
- Responsabilidad única por servicio

### Reutilización
- Centralizar funciones comunes
- Seguir principio DRY

### Testing
- Facilitar pruebas unitarias
- Permitir mocking de dependencias

## 5. middleware.mdc
Reglas para middleware global.

### Autenticación
- Verificar JWT en rutas protegidas
- Retornar 401 en fallos

### Logging
- Registrar requests/responses
- Excluir datos sensibles

### Validación
- Verificar Content-Type
- Validar datos requeridos

## 6. security.mdc
Reglas de seguridad de la aplicación.

### Protección CSRF
- Usar Flask-WTF/Flask-SeaSurf
- Validar tokens en forms

### XSS
- Jinja2 autoescape
- Sanitizar con Bleach

### JWT
- Algoritmos HS256/RS256
- Solo HTTPS

### Contraseñas
- Bcrypt/Argon2 para hashing
- Nunca en texto plano

## 7. loggin.mdc
Sistema de logging estructurado.

### Formato
- JSON estructurado
- Timestamps UTC ISO 8601
- Niveles DEBUG a CRITICAL

### Interfaz Web
- Vista HTML segura
- Filtros y paginación
- Solo acceso admin

### Privacidad
- No logs sensibles
- Escape XSS
- Timestamps sincronizados

## 8. config.mdc
Gestión de configuración y secretos.

### Entornos
- Development
- Testing
- Production

### Variables
- Usar variables de entorno
- No hardcodear secretos

### Estructura
- Clase base Config
- Clases derivadas por entorno

## 9. notifications.mdc
Sistema de notificaciones multicanal.

### APIs
- Twilio para WhatsApp
- Telegram Bot API

### Procesamiento
- Celery para async
- Reintentos exponenciales

### Seguridad
- No datos sensibles
- Credenciales en env

## 10. websockets.mdc
WebSockets con Flask-SocketIO.

### Redis
- Message queue distribuido
- URL en config

### Autenticación
- JWT en handshake
- Desconexión si inválido

### Eventos
- Nombres snake_case
- Salas por kiosko

## 11. cicd.mdc
Pipeline de integración/despliegue.

### Docker
- Multi-stage builds
- Python 3.11-slim
- Gunicorn+eventlet

### Tests
- Unitarios
- Integración
- Linting

### Despliegue
- Blue-green
- Versionado semántico

## 12. ai.mdc
Sistema de IA y autoentrenamiento.

### Autoentrenamiento
- Ciclos cada 24h
- Métricas y logs
- Alertas automáticas

### Dashboard
- Gráficos de evolución
- Control manual
- Acceso restringido

### Monitoreo
- Métricas en tiempo real
- Registro detallado
- Integración CI/CD 