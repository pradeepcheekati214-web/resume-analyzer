# API Notes

The full interactive OpenAPI (Swagger UI) documentation is available at:

- **Local dev**: http://localhost:8000/docs
- **ReDoc format**: http://localhost:8000/redoc

## Authentication

All protected endpoints require a Bearer token in the `Authorization` header:

```
Authorization: Bearer <access_token>
```

Obtain a token from `POST /api/v1/auth/login`.

## File Upload

The `POST /api/v1/resumes/upload` endpoint expects `multipart/form-data`.

```bash
curl -X POST http://localhost:8000/api/v1/resumes/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@my_resume.pdf"
```

## Rate Limits

In production (API Gateway): 1000 req/s sustained, 200 req/s burst.

## Error Format

```json
{
  "detail": "Human-readable error message"
}
```

Validation errors return:
```json
{
  "detail": "Validation error",
  "errors": [
    { "field": "body.email", "message": "value is not a valid email address" }
  ]
}
```
