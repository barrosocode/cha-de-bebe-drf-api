# Endpoints API

## Envelope

ALL HTTP responses MUST use the standard envelope. Never return raw DTOs, dicts, or ORM models directly from the controller/router.

The response body MUST be an object containing exactly the following top-level keys:

- `status` (integer): The corresponding HTTP status code.
- `message` (string): A message in Portuguese reflecting the result of the operation.
- `errors` (object): Must be an empty object on success. On failure, it must be a dictionary mapping field names to lists of error messages in Portuguese (e.g., mapping "email" to a list containing "O campo email deve ser válido").
- `<resource_key>` (object or array): The actual payload data. You MUST use the plural form plus an array for collections (e.g., `users`), and the singular form plus an object for a single item (e.g., `user`). NEVER use literal keys like "model" or "data".
- `pagination` (object): Required for list endpoints (detailed in the Pagination section below). Can be null or omitted for single-item responses.
- `error_code` (string or null): Must be null on success. On failure, it must be a stable string code (e.g., `VALIDATION_ERROR`, `HTTP_404`, `DOMAIN_EXCEPTION`).

```json
{
    "status": 200,
    "message": "Mensagem em português refletindo o resultado",
    "errors": {},
    "<resource_key>": {},
    "pagination": {},
    "error_code": null
}
```

## Auth

- POST /login
- POST /logout
- GET /me
- POST /refresh

## Guests

- POST /
- GET /
- GET /{UUID}
- PUT /{UUID}
- PATCH /{UUID}
- DELETE /{UUID}

### Permissions

- Usuário logado: all
- Não logado: apenas GETs com dados mascarados (detalhar depois)

## Gifts

- POST /
- GET /
- GET /{UUID}
- PUT /{UUID}
- PATCH /{UUID}
- DELETE /{UUID}

### Permissions

- Usuário logado: all
- Não logado: apenas GETs

## Tags

- POST /
- GET /
- GET /{UUID}
- PUT /{UUID}
- PATCH /{UUID}
- DELETE /{UUID}

### Permissions

- Usuário logado: all
