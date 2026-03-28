from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI

from app.internal.presentation.routers import router as recipes_router

api = NinjaAPI(title="Food App API", version="0.1.0")
api.add_router("/recipes", recipes_router)


@api.get("/health")
def healthcheck(request):
    return {"status": "ok"}

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),
]
