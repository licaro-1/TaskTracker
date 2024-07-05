from typing import Annotated

from fastapi import Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.pagination.schemas import PaginationParams


async def get_pagination_params(
    page: int = Query(ge=1, default=1),
    limit: int = Query(ge=1, default=20, le=100),
) -> PaginationParams:
    return PaginationParams(page=page, limit=limit)