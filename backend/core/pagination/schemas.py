from typing import Optional, Any, Sequence, List, TypeVar, Generic

from pydantic import BaseModel

TypeResp = TypeVar("TypeResp", bound=BaseModel)


class PaginationParams(BaseModel):
    page: int = 1
    limit: int = 100


class PageResponse(BaseModel):
    results: Sequence[Any] | List[Any]
    page: int
    pages_count: int
    limit: int
