from users.repository import UserRepository

from users.service import UserService


users_service = UserService(UserRepository)
