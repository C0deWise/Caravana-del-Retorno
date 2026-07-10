# Módulo `correos`

Servicio de envío de correos transaccionales del monolito modular, empezando
por el caso de uso de **recuperación de contraseña**.

## Estructura

```
correos/
├── api/v1/
│   ├── email.py        # Endpoints HTTP (presentación)
│   └── router.py        # Agrupa los routers v1 del módulo
├── docs/
│   └── email_docs.py     # Textos/metadata para Swagger
├── excepciones/
│   └── email_exceptions.py
├── models/
│   └── email.py          # Modelo de dominio EmailMessage
├── repositories/
│   └── email_repository.py  # Único punto que conoce fastapi-mail/SMTP
├── schemas/
│   └── email_schema.py   # DTOs de entrada/salida de la API
├── services/
│   └── email_service.py  # Reglas de negocio (orquesta repository)
├── plantillas/
│   └── email/
│       └── password_recovery.html
├── .env.example
└── README.md
```

Flujo de dependencias (una sola dirección):

```
api  ->  services  ->  repositories  ->  fastapi-mail (SMTP)
 |            |
 v            v
schemas     models
```
