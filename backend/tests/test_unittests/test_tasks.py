import pytest

from tasks.repository import TaskRepository


@pytest.fixture(scope="session")
def task_repository():
    repository = TaskRepository()
    return repository


@pytest.fixture(scope="session")
async def task(task_repository):
    task = await task_repository.create_one(data={
        "author_id": 1,
        "title": "Task Title",
        "description": "Task Description",
        "status_id": 1,
        "marked_users": []
    })
    return task


def test_object_success_create(task):
    assert task.author_id == 1
    assert task.title == "Task Title"
    assert task.description == "Task Description"
    assert task.status_id == 1
    assert task.marked_users == []


async def test_success_get_task_by_id(task_repository, task):
    assert await task_repository.get_one(id=task.id)


async def test_success_get_task_by_title(task_repository, task):
    assert await task_repository.get_one(title=task.title)


async def test_success_task_update(task_repository, task):
    upd_data = {
        "title": "Task Updated Title",
        "description": "Task Updated Description",
        "status_id": 2,
        "marked_users": []
    }
    upd_task = await task_repository.update_one(id=task.id, upd_data=upd_data)
    assert upd_task.title == upd_data["title"]
    assert upd_task.status_id == upd_data["status_id"]
    assert upd_task.description == upd_data["description"]
    assert upd_task.created_at != upd_task.updated_at


async def test_success_task_delete(task_repository, task):
    await task_repository.delete_one(id=task.id)
    assert not await task_repository.get_one(id=task.id)
