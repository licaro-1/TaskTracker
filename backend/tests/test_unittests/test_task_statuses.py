import pytest

from tasks.repository import TaskStatusRepository


@pytest.fixture(scope="session")
async def status_repository():
    repository = TaskStatusRepository()
    return repository


@pytest.fixture(scope="session")
async def status(status_repository: TaskStatusRepository):
    status = await status_repository.create_one(
        data={
            "name": "Test Status",
            "slug": "test-status"
        }
    )
    return status


async def test_success_create_object(status):
    assert status.name == "Test Status"
    assert status.slug == "test-status"


async def test_success_get_status_by_id(status_repository: TaskStatusRepository, status):
    assert await status_repository.get_one(id=status.id)


async def test_success_get_status_by_name(status_repository: TaskStatusRepository, status):
    assert await status_repository.get_one(name=status.name)


async def test_success_get_status_by_slug(status_repository: TaskStatusRepository, status):
    assert await status_repository.get_one(slug=status.slug)


async def test_success_status_update(status_repository: TaskStatusRepository, status):
    upd_data = {
        "name": "Updated Status",
        "slug": "upd-status"
    }
    await status_repository.update_one(id=status.id, data=upd_data)
    upd_status = await status_repository.get_one(id=status.id)
    assert upd_status.name == upd_data["name"]
    assert upd_status.slug == upd_data["slug"]


async def test_success_status_delete(status_repository: TaskStatusRepository, status):
    await status_repository.delete_one(id=status.id)
    assert not await status_repository.get_one(id=status.id)