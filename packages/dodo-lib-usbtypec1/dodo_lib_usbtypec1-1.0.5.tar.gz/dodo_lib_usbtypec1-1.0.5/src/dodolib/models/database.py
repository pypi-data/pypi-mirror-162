from uuid import UUID

from pydantic import BaseModel

__all__ = (
    'Unit',
    'Report',
    'Account',
    'StatisticsReportType',
    'ReportType',
)


class Unit(BaseModel):
    id: int
    name: str
    uuid: UUID
    account_name: str
    region: str


class Report(BaseModel):
    report_type: str
    chat_id: int
    unit_ids: list[int]


class Account(BaseModel):
    login: str
    password: str
    name: str


class ReportType(BaseModel):
    id: int
    name: str
    verbose_name: str


class StatisticsReportType(BaseModel):
    id: int
    name: str
    verbose_name: str
