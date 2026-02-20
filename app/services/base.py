from abc import ABC, abstractmethod


class DataProvider(ABC):
    @abstractmethod
    async def fetch(self, dataset: str, **kwargs):
        raise NotImplementedError
