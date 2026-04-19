from ninja import Router

from app.internal.presentation.handlers.recipe import list_recipes_handler
from app.internal.presentation.handlers.auth import JWTBearerAuth

router = Router(tags=["recipes"])
jwt_bearer_auth = JWTBearerAuth()


@router.get("/", auth=jwt_bearer_auth)
def list_recipes(request):
    return list_recipes_handler()
