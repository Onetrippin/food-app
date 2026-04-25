# food-app

Backend for a recipe web application built with Django, Django Ninja, PostgreSQL, Docker Compose, Nginx, and Poetry.

## Quick start

1. Create `.env` from `.env.example`.
2. Build and start containers:
   `make up`
3. Open:
   - API: `http://localhost:8080/api/`
   - Admin: `http://localhost:8080/admin/`

If you open the project through another host or port in development, add that origin to `DJANGO_CSRF_TRUSTED_ORIGINS`.

## Authentication

- `POST /api/auth/register` creates a new user and returns `access_token` and `refresh_token`
- `POST /api/auth/login` returns `access_token` and `refresh_token`
- `POST /api/auth/refresh` returns a new `access_token`
- `GET /api/auth/me` requires `Authorization: Bearer <access_token>`
- `POST /api/auth/password/change/request` sends a code to the authenticated user's email
- `POST /api/auth/password/change/confirm` accepts the code and the new password
- `DELETE /api/auth/account` deletes the authenticated account
- `GET /api/recipes/` also requires `Authorization: Bearer <access_token>`
- `GET /api/recipes/{recipe_id}` returns a specific recipe
- `GET /api/recipes/search?q=...` searches recipes by title and description

For development, the default email backend writes outgoing messages to container logs. To send real emails, configure SMTP variables in `.env`.

## Project structure

```text
src/
  app/
    internal/
      data/
      domain/
      presentation/
    migrations/
  config/
  manage.py
```
