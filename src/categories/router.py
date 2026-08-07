import uuid

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from src.auth.dependencies import get_current_admin
from src.categories.dependencies import get_category_service
from src.categories.exceptions import (
    CategoryAlreadyExistsError,
    CategoryNotFoundError,
)
from src.categories.schemas import (
    CategoryCreate,
    CategoryResponse,
    CategoryUpdate,
)
from src.categories.service import CategoryService
from src.users.models import User


router = APIRouter(
    prefix="/categories",
    tags=["Categories"],
)


@router.get(
    "",
    response_model=list[CategoryResponse],
    status_code=status.HTTP_200_OK,
)
async def get_categories(
    service: CategoryService = Depends(
        get_category_service
    ),
):
    return await service.get_categories()


@router.get(
    "/admin",
    response_model=list[CategoryResponse],
    status_code=status.HTTP_200_OK,
)
async def get_all_categories(
    current_admin: User = Depends(
        get_current_admin
    ),
    service: CategoryService = Depends(
        get_category_service
    ),
):
    return await service.get_all_categories()


@router.post(
    "",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_category(
    data: CategoryCreate,
    current_admin: User = Depends(
        get_current_admin
    ),
    service: CategoryService = Depends(
        get_category_service
    ),
):
    try:
        return await service.create_category(
            data=data
        )

    except CategoryAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Категория с таким названием или slug уже существует!",
        )


@router.patch(
    "/{category_id}",
    response_model=CategoryResponse,
    status_code=status.HTTP_200_OK,
)
async def update_category(
    category_id: uuid.UUID,
    data: CategoryUpdate,
    current_admin: User = Depends(
        get_current_admin
    ),
    service: CategoryService = Depends(
        get_category_service
    ),
):
    try:
        return await service.update_category(
            category_id=category_id,
            data=data,
        )

    except CategoryNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Категория не найдена!",
        )