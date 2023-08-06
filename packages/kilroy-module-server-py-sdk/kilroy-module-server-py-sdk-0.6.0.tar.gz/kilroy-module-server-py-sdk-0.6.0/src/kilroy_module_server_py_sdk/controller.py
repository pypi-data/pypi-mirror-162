import json
from abc import ABC, abstractmethod
from typing import (
    AsyncIterable,
    Awaitable,
    Callable,
    Type,
    TypeVar,
)

from aiostream import stream
from asyncstdlib import enumerate
from kilroy_module_py_shared import (
    Config,
    ConfigNotification,
    ConfigSchema,
    ConfigSetReply,
    ConfigSetRequest,
    FitPostsReply,
    FitPostsRequest,
    FitScoresReply,
    FitScoresRequest,
    GenerateReply,
    GenerateRequest,
    JSONSchema,
    MetricsInfo,
    MetricsNotification,
    PostSchema,
    Status,
    StatusEnum,
    StatusNotification,
    StepReply,
    StepRequest,
)
from kilroy_ws_server_py_sdk import (
    Controller,
    Get,
    JSON,
    NotInitializedError,
    ParameterGetError,
    ParameterSetError,
    Request,
    RequestStreamIn,
    RequestStreamOut,
    Subscribe,
)
from pydantic import BaseModel

from kilroy_module_server_py_sdk.errors import (
    PARAMETER_GET_ERROR,
    PARAMETER_SET_ERROR,
    STATE_NOT_READY_ERROR,
)
from kilroy_module_server_py_sdk.module import Module

M = TypeVar("M", bound=BaseModel)
N = TypeVar("N", bound=BaseModel)


class BaseController(Controller, ABC):
    @staticmethod
    async def _handle_get(fn: Callable[[], Awaitable[M]]) -> JSON:
        payload = await fn()
        return json.loads(payload.json())

    @staticmethod
    async def _handle_subscribe(
        fn: Callable[[], AsyncIterable[M]]
    ) -> AsyncIterable[JSON]:
        async for payload in fn():
            yield json.loads(payload.json())

    @staticmethod
    async def _handle_request(
        fn: Callable[[Awaitable[N]], Awaitable[M]],
        payload: Awaitable[JSON],
        model: Type[N],
    ) -> JSON:
        async def make_request(payload: Awaitable[JSON], model: Type[N]) -> N:
            return model.parse_obj(await payload)

        request = make_request(payload, model)

        try:
            reply = await fn(request)
            return json.loads(reply.json())
        finally:
            request.close()

    @staticmethod
    async def _handle_request_stream_out(
        fn: Callable[[Awaitable[N]], AsyncIterable[M]],
        payload: Awaitable[JSON],
        model: Type[N],
    ) -> AsyncIterable[JSON]:
        async def make_request(payload: Awaitable[JSON], model: Type[N]) -> N:
            return model.parse_obj(await payload)

        request = make_request(payload, model)

        try:
            async for reply in fn(request):
                yield json.loads(reply.json())
        finally:
            request.close()

    @staticmethod
    async def _handle_request_stream_in(
        fn: Callable[[AsyncIterable[N]], Awaitable[M]],
        request_payloads: AsyncIterable[JSON],
        request_model: Type[N],
    ) -> JSON:
        async def make_requests(
            payloads: AsyncIterable[JSON],
        ) -> AsyncIterable[N]:
            async for payload in payloads:
                yield request_model.parse_obj(payload)

        reply = await fn(make_requests(request_payloads))
        return json.loads(reply.json())

    @Get("/post/schema")
    async def _handle_post_schema(self) -> JSON:
        return await self._handle_get(self.post_schema)

    @Get("/status")
    async def _handle_status(self) -> JSON:
        return await self._handle_get(self.status)

    @Subscribe("/status/watch")
    async def _handle_watch_status(self) -> AsyncIterable[JSON]:
        async for payload in self._handle_subscribe(self.watch_status):
            yield payload

    @Get("/config")
    async def _handle_config(self) -> JSON:
        return await self._handle_get(self.config)

    @Get("/config/schema")
    async def _handle_config_schema(self) -> JSON:
        return await self._handle_get(self.config_schema)

    @Subscribe("/config/watch")
    async def _handle_watch_config(self) -> AsyncIterable[JSON]:
        async for payload in self._handle_subscribe(self.watch_config):
            yield payload

    @Request("/config/set")
    async def _handle_set_config(self, data: Awaitable[JSON]) -> JSON:
        return await self._handle_request(
            self.set_config, data, ConfigSetRequest
        )

    @RequestStreamOut("/generate")
    async def _handle_generate(
        self, data: Awaitable[JSON]
    ) -> AsyncIterable[JSON]:
        async for payload in self._handle_request_stream_out(
            self.generate, data, GenerateRequest
        ):
            yield payload

    @RequestStreamIn("/fit/posts")
    async def _handle_fit_posts(self, data: AsyncIterable[JSON]) -> JSON:
        return await self._handle_request_stream_in(
            self.fit_posts, data, FitPostsRequest
        )

    @Request("/fit/scores")
    async def _handle_fit_scores(self, data: Awaitable[JSON]) -> JSON:
        return await self._handle_request(
            self.fit_scores, data, FitScoresRequest
        )

    @Request("/step")
    async def _handle_step(self, data: Awaitable[JSON]) -> JSON:
        return await self._handle_request(self.step, data, StepRequest)

    @Get("/metrics/info")
    async def _handle_metrics_info(self) -> JSON:
        return await self._handle_get(self.metrics_info)

    @Subscribe("/metrics/watch")
    async def _handle_watch_metrics(
        self,
    ) -> AsyncIterable[JSON]:

        async for payload in self._handle_subscribe(self.watch_metrics):
            yield payload

    @abstractmethod
    async def post_schema(self) -> PostSchema:
        pass

    @abstractmethod
    async def status(self) -> Status:
        pass

    @abstractmethod
    def watch_status(self) -> AsyncIterable[StatusNotification]:
        pass

    @abstractmethod
    async def config(self) -> Config:
        pass

    @abstractmethod
    async def config_schema(self) -> ConfigSchema:
        pass

    @abstractmethod
    def watch_config(self) -> AsyncIterable[ConfigNotification]:
        pass

    @abstractmethod
    async def set_config(
        self, request: Awaitable[ConfigSetRequest]
    ) -> ConfigSetReply:
        pass

    @abstractmethod
    def generate(
        self, request: Awaitable[GenerateRequest]
    ) -> AsyncIterable[GenerateReply]:
        pass

    @abstractmethod
    async def fit_posts(
        self, requests: AsyncIterable[FitPostsRequest]
    ) -> FitPostsReply:
        pass

    @abstractmethod
    async def fit_scores(
        self, request: Awaitable[FitScoresRequest]
    ) -> FitScoresReply:
        pass

    @abstractmethod
    async def step(self, request: Awaitable[StepRequest]) -> StepReply:
        pass

    @abstractmethod
    async def metrics_info(self) -> MetricsInfo:
        pass

    @abstractmethod
    def watch_metrics(self) -> AsyncIterable[MetricsNotification]:
        pass


class ModuleController(BaseController):
    def __init__(self, module: Module) -> None:
        super().__init__()
        self._module = module

    async def post_schema(self) -> PostSchema:
        return PostSchema(post_schema=self._module.post_schema)

    async def status(self) -> Status:
        ready = await self._module.state.ready.fetch()
        status = StatusEnum.ready if ready else StatusEnum.loading
        return Status(status=status)

    async def watch_status(self) -> AsyncIterable[StatusNotification]:
        async for ready in self._module.state.ready.subscribe():
            status = StatusEnum.ready if ready else StatusEnum.loading
            yield StatusNotification(status=status)

    async def config(self) -> Config:
        try:
            return Config(config=await self._module.config.json.fetch())
        except NotInitializedError as e:
            raise STATE_NOT_READY_ERROR from e

    async def config_schema(self) -> ConfigSchema:
        return ConfigSchema(config_schema=JSONSchema(self._module.schema))

    async def watch_config(self) -> AsyncIterable[ConfigNotification]:
        async for config in self._module.config.json.subscribe():
            yield ConfigNotification(config=config)

    async def set_config(
        self, request: Awaitable[ConfigSetRequest]
    ) -> ConfigSetReply:
        try:
            config = await self._module.config.set((await request).config)
        except NotInitializedError as e:
            raise STATE_NOT_READY_ERROR from e
        except ParameterGetError as e:
            raise PARAMETER_GET_ERROR from e
        except ParameterSetError as e:
            raise PARAMETER_SET_ERROR from e
        return ConfigSetReply(config=config)

    async def generate(
        self, request: Awaitable[GenerateRequest]
    ) -> AsyncIterable[GenerateReply]:
        request = await request
        async for number, (post_id, post) in enumerate(
            self._module.generate(request.number_of_posts)
        ):
            yield GenerateReply(post_number=number, post_id=post_id, post=post)

    async def fit_posts(
        self, requests: AsyncIterable[FitPostsRequest]
    ) -> FitPostsReply:
        async def posts():
            async for request in requests:
                yield request.post

        await self._module.fit_posts(posts())
        return FitPostsReply(success=True)

    async def fit_scores(
        self, request: Awaitable[FitScoresRequest]
    ) -> FitScoresReply:
        request = await request
        scores = [(score.post_id, score.score) for score in request.scores]
        await self._module.fit_score(scores)
        return FitScoresReply(success=True)

    async def step(self, request: Awaitable[StepRequest]) -> StepReply:
        await request
        await self._module.step()
        return StepReply(success=True)

    async def metrics_info(self) -> MetricsInfo:
        return MetricsInfo(
            metrics={
                metric.name: metric.info for metric in self._module.metrics
            }
        )

    async def watch_metrics(self) -> AsyncIterable[MetricsNotification]:
        combine = stream.merge(
            *(metric.watch() for metric in self._module.metrics)
        )

        async with combine.stream() as streamer:
            async for data in streamer:
                yield data
