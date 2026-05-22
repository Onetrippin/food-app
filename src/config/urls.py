from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI

from app.internal.presentation.routers import auth_router, payment_router, recipe_router

api = NinjaAPI(title="Food App API", version="0.1.0")
api.add_router("/auth", auth_router)
api.add_router("/payments", payment_router)
api.add_router("/recipes", recipe_router)


@api.get("/health")
def healthcheck(request):
    return {"status": "ok"}

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),
]
