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
- `POST /api/auth/author-application` submits an application for author publishing rights
- `GET /api/auth/author-application` returns the current user's author application status
- `PUT /api/auth/author-profile` updates author subscription price and enables or disables subscriptions after approval
- `GET /api/recipes/` also requires `Authorization: Bearer <access_token>`
- `GET /api/recipes/{recipe_id}` returns a specific recipe
- `GET /api/recipes/search?q=...` searches recipes by title and description
- `GET /api/recipes/search/by-ingredients?ingredients=egg,milk,butter` returns recipes that can be prepared from the provided ingredients
- `POST /api/recipes/` creates a recipe for the authenticated user
- recipe publication is unavailable by default; `is_published=true` works only for staff or users with an approved author application
- `PUT /api/recipes/{recipe_id}` edits a recipe; only the author or staff can do that
- `DELETE /api/recipes/{recipe_id}` deletes a recipe; only the author or staff can do that
- `POST /api/recipes/{recipe_id}/favorite` adds a recipe to favorites
- `DELETE /api/recipes/{recipe_id}/favorite` removes a recipe from favorites
- `POST /api/recipes/{recipe_id}/like` adds a like to a published recipe
- `DELETE /api/recipes/{recipe_id}/like` removes a like
- `GET /api/recipes/favorites` returns the authenticated user's favorite recipes
- `GET /api/recipes/analytics` returns analytics for the authenticated user's recipes
- recipe responses now include `price_amount` and `price_currency`

## Payments

- `POST /api/payments/recipes/{recipe_id}/checkout` creates a YooKassa payment for a paid recipe
- `POST /api/payments/authors/{author_id}/subscription/checkout` creates a YooKassa payment for a paid author subscription
- `GET /api/payments/me/recipe-purchases` returns purchased recipes
- `GET /api/payments/me/author-subscriptions` returns author subscriptions
- `POST /api/payments/yookassa/webhook` processes YooKassa webhooks

Recipe access rules:
- free published recipes are available to everyone with JWT auth
- paid recipes require either a direct purchase or an active paid subscription to that recipe's author
- authors and staff always keep access to their own recipes

Operational notes:
- author applications are approved or rejected manually in Django admin
- before using checkout endpoints, configure `YOOKASSA_SHOP_ID`, `YOOKASSA_SECRET_KEY`, and `YOOKASSA_RETURN_URL` in `.env`

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
