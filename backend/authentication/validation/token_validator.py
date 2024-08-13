
from authentication.utils import TOKEN_TYPE
from core.exceptions.users import UnauthorizedError


async def validate_token_type(payload: dict, expected_token_type: str) -> bool:
    token_type = payload.get(TOKEN_TYPE)
    if token_type == expected_token_type:
        return True
    raise UnauthorizedError(f"invalid token type {token_type!r} expected {expected_token_type!r}")
