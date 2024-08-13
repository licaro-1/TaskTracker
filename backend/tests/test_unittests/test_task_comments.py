import pytest

from tasks.repository import TaskCommentRepository


@pytest.fixture(scope="session")
def comment_repository():
    repository = TaskCommentRepository()
    return repository


@pytest.fixture(scope="session")
async def comment(comment_repository):
    comment = await comment_repository.create_one(data={
        "author_id": 2,
        "task_id": 1,
        "text": "Test Comment"
    })
    return comment


def test_success_task_create(comment):
    assert comment.author_id == 2
    assert comment.task_id == 1
    assert comment.text == "Test Comment"


async def test_success_get_comment_by_id(comment_repository, comment):
    assert await comment_repository.get_one(id=comment.id)


async def test_success_get_comment_by_title(comment_repository, comment):
    assert await comment_repository.get_one(text=comment.text)


async def test_success_comment_update(comment_repository, comment):
    upd_data = {"text": "Updated Text"}
    await comment_repository.update_one(id=comment.id, data=upd_data)
    upd_comment = await comment_repository.get_one(id=comment.id)
    assert upd_comment.text == upd_data["text"]
    assert upd_comment.created_at != upd_comment.updated_at

