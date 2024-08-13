from repositories.sqlalchemy import SqlAlchemyRepository
from core.db.db_helper import db_helper
from authentication.utils import hash_password
from users.models import User


class UserRepository(SqlAlchemyRepository):
    model = User

    async def create_one(self, data: dict) -> model:
        if "hashed_password" in data:
            return await super().create_one(data)
        hashed_password = await hash_password(data.pop("password"))
        async with db_helper.session_factory() as session:
            user = User(**data, hashed_password=hashed_password)
            session.add(user)
            await session.commit()
        return user
