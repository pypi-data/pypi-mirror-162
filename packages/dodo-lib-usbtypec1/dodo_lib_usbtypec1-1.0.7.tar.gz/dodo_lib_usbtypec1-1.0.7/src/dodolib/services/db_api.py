from typing import Iterable

from pydantic import parse_obj_as

from .base import BaseHTTPService
from .. import models
from ..utils import exceptions

__all__ = (
    'DatabaseClient',
)


class DatabaseClient(BaseHTTPService):
    service_name = 'DATABASE_API'

    async def get_units(
            self,
            region: str | None = None,
            limit: int | None = None,
            skip: int | None = None,
    ) -> list[models.Unit]:
        params = {}
        if region is not None:
            params['region'] = region
        if limit is not None:
            params['limit'] = limit
        if skip is not None:
            params['skip'] = skip

        response = await self._client.get('/units/', params=params)
        if response.is_error:
            raise exceptions.DatabaseAPIError
        return parse_obj_as(list[models.Unit], response.json())

    async def get_regions(self) -> list[str]:
        response = await self._client.get('/units/regions/')
        if response.is_error:
            raise exceptions.DatabaseAPIError
        return response.json()

    async def get_reports(
            self,
            limit: int | None = None,
            skip: int | None = None,
            report_type: str | None = None,
            chat_id: int | None = None,
    ) -> list[models.Report]:
        params = {}
        if limit is not None:
            params['limit'] = limit
        if skip is not None:
            params['skip'] = skip
        if report_type is not None:
            params['report_type'] = report_type
        if chat_id is not None:
            params['chat_id'] = chat_id

        response = await self._client.get('/reports/', params=params)
        if response.is_error:
            raise exceptions.DatabaseAPIError
        return parse_obj_as(list[models.Report], response.json())

    async def add_unit_ids_to_report(
            self,
            report_type: str,
            chat_id: int,
            unit_ids: Iterable[int],
    ):
        body = {
            'report_type': report_type,
            'chat_id': chat_id,
            'unit_ids': tuple(unit_ids),
        }
        response = await self._client.post('/reports/', json=body)
        if response.is_error:
            raise exceptions.DatabaseAPIError

    async def remove_unit_ids_from_report(
            self,
            report_type: str,
            chat_id: int,
            unit_ids: Iterable[int],
    ):
        body = {
            'report_type': report_type,
            'chat_id': chat_id,
            'unit_ids': tuple(unit_ids),
        }
        response = await self._client.request('DELETE', url='/reports/', json=body)
        if response.is_error:
            raise exceptions.DatabaseAPIError

    async def get_accounts(
            self,
            limit: int | None = None,
            skip: int | None = None,
    ) -> list[models.Account]:
        params = {}
        if limit is not None:
            params['limit'] = limit
        if skip is not None:
            params['skit'] = skip
        response = await self._client.get('/accounts/', params=params)
        if response.is_error:
            raise exceptions.DatabaseAPIError
        return parse_obj_as(list[models.Account], response.json())

    async def get_report_types(
            self,
            limit: int | None = None,
            skip: int | None = None,
    ) -> list[models.ReportType]:
        params = {}
        if limit is not None:
            params['limit'] = limit
        if skip is not None:
            params['skit'] = skip
        response = await self._client.get('/report-types/', params=params)
        if response.is_error:
            raise exceptions.DatabaseAPIError
        return parse_obj_as(list[models.ReportType], response.json())

    async def get_statistics_report_types(
            self,
            limit: int | None = None,
            skip: int | None = None,
    ) -> list[models.StatisticsReportType]:
        params = {}
        if limit is not None:
            params['limit'] = limit
        if skip is not None:
            params['skit'] = skip
        response = await self._client.get('/report-types/statistics/', params=params)
        if response.is_error:
            raise exceptions.DatabaseAPIError
        return parse_obj_as(list[models.StatisticsReportType], response.json())
