from core.exceptions import users as user_exc


async def validate_create_password(password: str):
    if len(password) < 8:
        raise user_exc.SmallUserPasswordError
