from fastapi import APIRouter

from pandahub.api.internal import settings
from pandahub.api.internal.users import fastapi_users

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

router.include_router(
    fastapi_users.get_users_router(
        requires_verification=settings.EMAIL_VERIFICATION_REQUIRED),
)
