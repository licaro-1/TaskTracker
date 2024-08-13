import json
import asyncio
from pathlib import Path

import click
from sqlalchemy import select

from core.settings import BASE_DIR
from core.db.db_helper import db_helper
from authentication.utils import hash_password
from users.models import User
from tasks.models import TaskStatus

LOAD_DATA_DIR: Path = BASE_DIR / "core" / "utils" / "load_data"

LOOP = asyncio.get_event_loop()


@click.group()
def commands():
    pass


async def load_to_db(filename: str | Path, model) -> int:
    create_counter = 0
    with open(filename, encoding="utf-8") as f:
        data = json.load(f)
        async with db_helper.session_factory() as session:
            for obj in data:
                if model == User:
                    hashed_password = await hash_password(obj.pop("password"))
                    obj["hashed_password"] = hashed_password
                obj_in_db = await session.scalar(select(model).filter_by(**obj))
                # if object already in db
                if not obj_in_db:
                    model_obj = model(**obj)
                    session.add(model_obj)
                    create_counter += 1
                    await session.commit()
    return create_counter


@click.command("load_superusers")
def load_superusers_command():
    """Function of load superusers to database."""
    superuser__data_path = LOAD_DATA_DIR / "superusers.json"
    created = LOOP.run_until_complete(load_to_db(superuser__data_path, User))
    click.echo(f"Загружено супер-пользователей: {created!r}")


@click.command("load_users")
def load_users_command():
    """Function of load users to database."""
    user_data_path = LOAD_DATA_DIR / "users.json"
    created = LOOP.run_until_complete(load_to_db(user_data_path, User))
    click.echo(f"Загружено пользователей: {created!r}")


@click.command("load_statuses")
def load_statuses_command():
    """Function of load statuses to database."""
    statuses_data_path = LOAD_DATA_DIR / "statuses.json"
    created = LOOP.run_until_complete(load_to_db(statuses_data_path, TaskStatus))
    click.echo(f"Загружено статусов: {created!r}")


commands.add_command(load_superusers_command)
commands.add_command(load_users_command)
commands.add_command(load_statuses_command)


if __name__ == "__main__":
    commands()
