from typing import Sequence, Optional,List, Any

from .schemas import PageResponse


def format_to_pagination_scheme(
    results: Optional[Sequence[Any] | List[Any]],
    pages_count: int,
    page: int,
    limit: int,
):
    return PageResponse(
        results=results,
        page=page,
        pages_count=pages_count,
        limit=limit,
    )
