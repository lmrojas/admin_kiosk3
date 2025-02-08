# Documentación de APIs

## Auth Service (Puerto 5001)
### POST /auth/login
Login de usuario
- Request: `{"username": "string", "password": "string"}`
- Response: `{"token": "string"}`

### POST /auth/register
Registro de usuario
- Request: `{"username": "string", "password": "string", "email": "string"}`
- Response: `{"message": "Usuario registrado"}`

## Kiosk Service (Puerto 5002)
### GET /kiosks
Listar kioskos
- Response: `[{"id": int, "name": "string", "location": "string"}]`

### POST /kiosks
Crear kiosko
- Request: `{"name": "string", "location": "string"}`
- Response: `{"id": int, "message": "Kiosko creado"}`

[Continuar con los demás endpoints...] 