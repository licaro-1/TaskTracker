from tasks.service import TaskService
from tasks.repository import TaskRepository, TaskStatusRepository, TaskCommentRepository
from users.repository import UserRepository

tasks_service = TaskService(TaskRepository, TaskStatusRepository, UserRepository, TaskCommentRepository)
