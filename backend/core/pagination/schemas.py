from typing import Optional, Any, Sequence, List

from pydantic import BaseModel


class PaginationParams(BaseModel):
    page: int = 1
    limit: int = 100


class PageResponse(BaseModel):
    results: Sequence[Any] | List[Any]
    page: int
    pages_count: int
    limit: int
