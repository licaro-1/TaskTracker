from sqlalchemy import update

from repositories.sqlalchemy import SqlAlchemyRepository
from core.db.db_helper import db_helper
from users.models import User


class UserRepository(SqlAlchemyRepository):
    model = User
