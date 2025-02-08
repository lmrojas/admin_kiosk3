# API Reference

## Auth Service (5001)
### POST /auth/login
Login de usuario
- Request: { "username": string, "password": string }
- Response: { "token": string }

### POST /auth/register
Registro de nuevo usuario
- Request: { "username": string, "password": string, "email": string }
- Response: { "id": int, "username": string }

## Kiosk Service (5002)
### GET /kiosks
Lista todos los kioscos
- Response: [{ "id": int, "name": string, "status": string }]

### POST /kiosks
Crea nuevo kiosko
- Request: { "name": string, "location": string }
- Response: { "id": int, "name": string }

## Payment Service (5003)
### POST /payments
Procesa un pago
- Request: { "amount": float, "method": string }
- Response: { "id": int, "status": string } 