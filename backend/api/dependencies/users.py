from users.repositories import UserRepository

from users.services import UserService


users_service = UserService(UserRepository)
