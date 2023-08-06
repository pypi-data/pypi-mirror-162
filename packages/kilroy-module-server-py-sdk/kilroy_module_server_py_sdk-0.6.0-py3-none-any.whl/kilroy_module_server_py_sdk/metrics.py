from abc import ABC, abstractmethod
from typing import AsyncIterable, Generic, TypeVar

from kilroy_module_py_shared import (
    SeriesMetricInfo,
    SeriesMetricNotificationData,
    TimeseriesMetricInfo,
    TimeseriesMetricNotificationData,
)
from kilroy_ws_server_py_sdk import Categorizable, Observable, classproperty

MetricInfoType = TypeVar("MetricInfoType")
MetricNotificationType = TypeVar("MetricNotificationType")


class Metric(
    Categorizable, Generic[MetricInfoType, MetricNotificationType], ABC
):
    _observable: Observable[MetricNotificationType]

    def __init__(self) -> None:
        super().__init__()
        self._observable = Observable()

    @classproperty
    def category(cls) -> str:
        return cls.name

    @classproperty
    @abstractmethod
    def name(cls) -> str:
        pass

    @classproperty
    @abstractmethod
    def info(cls) -> MetricInfoType:
        pass

    async def report(self, data: MetricNotificationType) -> None:
        await self._observable.set(data)

    async def watch(self) -> AsyncIterable[MetricNotificationType]:
        async for data in self._observable.subscribe():
            yield data


class SeriesMetric(
    Metric[SeriesMetricInfo, SeriesMetricNotificationData], ABC
):
    pass


class TimeseriesMetric(
    Metric[TimeseriesMetricInfo, TimeseriesMetricNotificationData], ABC
):
    pass
