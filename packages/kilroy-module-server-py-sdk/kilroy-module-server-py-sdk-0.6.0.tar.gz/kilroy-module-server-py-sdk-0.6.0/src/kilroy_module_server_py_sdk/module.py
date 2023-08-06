from abc import ABC, abstractmethod
from typing import AsyncIterable, Generic, List, Set, Tuple, TypeVar
from uuid import UUID

from kilroy_module_py_shared import JSON, JSONSchema
from kilroy_ws_server_py_sdk import Configurable

from kilroy_module_server_py_sdk.metrics import Metric

StateType = TypeVar("StateType")


class Module(Configurable[StateType], Generic[StateType], ABC):
    @property
    @abstractmethod
    def post_schema(self) -> JSONSchema:
        pass

    @property
    @abstractmethod
    def metrics(self) -> Set[Metric]:
        pass

    @abstractmethod
    def generate(self, n: int) -> AsyncIterable[Tuple[UUID, JSON]]:
        pass

    @abstractmethod
    async def fit_posts(self, posts: AsyncIterable[JSON]) -> None:
        pass

    @abstractmethod
    async def fit_score(self, scores: List[Tuple[UUID, float]]) -> None:
        pass

    @abstractmethod
    async def step(self) -> None:
        pass
