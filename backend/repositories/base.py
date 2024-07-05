from abc import ABC, abstractmethod


class AbstractRepository:
    @abstractmethod
    async def create_one(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def get_one(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def update_one(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def delete_one(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def get_multi(self, *args, **kwargs):
        raise NotImplementedError
