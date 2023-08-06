"""
- Statistics:
    - By tokens and unit UUIDs:
        - OrdersHandoverTimeStatistics
            - UnitOrdersHandoverTime
        - DeliverySpeedStatistics
            - UnitDeliverySpeed
    - By cookies, unit ids and unit names:
        - BeingLateCertificatesStatistics
            - UnitBeingLateCertificatesTodayAndWeekBefore
        - BonusSystemStatistics
            - UnitBonusSystem
    - By cookies and unit ids:
        - RevenueStatistics
            - UnitsRevenueMetadata
            - RevenueForTodayAndWeekBeforeStatistics
        - KitchenPerformanceStatistics
            - UnitKitchenPerformance
        - DeliveryPerformanceStatistics
            - UnitDeliveryPerformance
        - HeatedShelfStatistics
            - UnitHeatedShelf
        - CouriersStatistics
            - UnitCouriers
        - KitchenProductionStatistics
            - UnitKitchenProduction
        - HeatedShelfOrdersAndCouriersStatistics
            - UnitHeatedShelfOrdersAndCouriers

- Stop sales:
    - StopSale
        - StopSaleByToken
            - StopSaleByIngredients
            - StopSaleByProduct
            - StopSaleBySalesChannels
        - StopSaleBySectors
        - StopSaleByStreets


"""
from enum import Enum
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field, validator

from models.aliases import UnitIdAndName

__all__ = (
    'DeliverySpeedStatistics',
    'StockBalanceStatistics',
    'BonusSystemStatistics',
    'CouriersStatistics',
    'RevenueStatistics',
    'HeatedShelfStatistics',
    'DeliveryPerformanceStatistics',
    'KitchenPerformanceStatistics',
    'KitchenProductionStatistics',
    'HeatedShelfOrdersAndCouriersStatistics',
    'BeingLateCertificatesStatistics',
    'OrdersHandoverTimeStatistics',
    'RevenueForTodayAndWeekBeforeStatistics',

    'UnitCouriers',
    'UnitIdAndName',
    'UnitBonusSystem',
    'UnitOrdersHandoverTime',
    'UnitDeliverySpeed',
    'UnitsRevenueMetadata',
    'UnitHeatedShelf',
    'UnitKitchenProduction',
    'UnitDeliveryPerformance',
    'UnitKitchenPerformance',
    'UnitBeingLateCertificates',
    'UnitHeatedShelfOrdersAndCouriers',

    'StopSale',
    'StopSaleByToken',
    'StopSaleByIngredients',
    'StopSaleByProduct',
    'StopSaleBySalesChannels',
    'StopSaleBySectors',
    'StopSaleByStreets',
    'SalesChannel',

    'OrderByUUID',
    'CheatedOrders',
    'CheatedOrder',
    'StockBalance',
)


# Statistics
# Models by tokens and unit UUIDs

class SalesChannel(Enum):
    DINE_IN = 'Dine-in'
    TAKEAWAY = 'Takeaway'
    DELIVERY = 'Delivery'


class UnitOrdersHandoverTime(BaseModel):
    unit_uuid: UUID
    unit_name: str
    average_tracking_pending_time: int
    average_cooking_time: int
    average_heated_shelf_time: int
    sales_channels: list[SalesChannel]


class OrdersHandoverTimeStatistics(BaseModel):
    units: list[UnitOrdersHandoverTime]
    error_unit_uuids: list[UUID]


class UnitDeliverySpeed(BaseModel):
    unit_uuid: UUID
    unit_name: str
    average_cooking_time: int
    average_delivery_order_fulfillment_time: int
    average_heated_shelf_time: int
    average_order_trip_time: int


class DeliverySpeedStatistics(BaseModel):
    units: list[UnitDeliverySpeed]
    error_unit_uuids: list[UUID]


# Models by cookies, unit ids and names

class UnitBeingLateCertificates(BaseModel):
    unit_id: int
    unit_name: str
    certificates_today_count: int
    certificates_week_before_count: int


class BeingLateCertificatesStatistics(BaseModel):
    units: list[UnitBeingLateCertificates]
    error_unit_ids_and_names: list[UnitIdAndName]


class UnitBonusSystem(BaseModel):
    unit_name: str
    orders_with_phone_numbers_count: int
    orders_with_phone_numbers_percent: float
    total_orders_count: int


class BonusSystemStatistics(BaseModel):
    units: list[UnitBonusSystem]
    error_unit_ids_and_names: list[UnitIdAndName]


# Models by cookies and unit ids

class UnitsRevenueMetadata(BaseModel):
    total_revenue_today: int
    total_revenue_week_before: int
    delta_from_week_before: float


class RevenueForTodayAndWeekBeforeStatistics(BaseModel):
    unit_id: int
    today: int
    week_before: int
    delta_from_week_before: float


class RevenueStatistics(BaseModel):
    units: list[RevenueForTodayAndWeekBeforeStatistics]
    metadata: UnitsRevenueMetadata
    error_unit_ids: list[int]


class UnitKitchenPerformance(BaseModel):
    unit_id: int
    revenue_per_hour: int
    revenue_delta_from_week_before: int


class KitchenPerformanceStatistics(BaseModel):
    units: list[UnitKitchenPerformance]
    error_unit_ids: list[int]


class UnitDeliveryPerformance(BaseModel):
    unit_id: int
    orders_for_courier_count_per_hour_today: float
    orders_for_courier_count_per_hour_week_before: float
    delta_from_week_before: int


class DeliveryPerformanceStatistics(BaseModel):
    units: list[UnitDeliveryPerformance]
    error_unit_ids: list[int]


class UnitHeatedShelf(BaseModel):
    unit_id: int
    average_awaiting_time: int
    awaiting_orders_count: int


class HeatedShelfStatistics(BaseModel):
    units: list[UnitHeatedShelf]
    error_unit_ids: list[int]


class UnitCouriers(BaseModel):
    unit_id: int
    in_queue_count: int
    total_count: int


class CouriersStatistics(BaseModel):
    units: list[UnitCouriers]
    error_unit_ids: list[int]


class UnitKitchenProduction(BaseModel):
    unit_id: int
    average_cooking_time: int


class KitchenProductionStatistics(BaseModel):
    units: list[UnitKitchenProduction]
    error_unit_ids: list[int]


class UnitHeatedShelfOrdersAndCouriers(BaseModel):
    unit_id: int
    awaiting_orders_count: int
    in_queue_count: int
    total_count: int


class HeatedShelfOrdersAndCouriersStatistics(BaseModel):
    units: list[UnitHeatedShelfOrdersAndCouriers]
    error_unit_ids: list[int]


# Stop sales

class StopSale(BaseModel):
    unit_name: str
    started_at: datetime
    ended_at: datetime | None
    staff_name_who_stopped: str
    staff_name_who_resumed: str | None


# New API
class StopSaleByToken(StopSale):
    unit_uuid: UUID = Field(alias='unit_id')
    reason: str


class StopSaleByIngredients(StopSaleByToken):
    ingredient_name: str


class StopSaleByProduct(StopSaleByToken):
    product_name: str


class StopSaleBySalesChannels(StopSaleByToken):
    sales_channel_name: str


# Old API (Dodo IS)
class StopSaleBySectors(StopSale):
    sector: str


class StopSaleByStreets(StopSale):
    sector: str
    street: str


class OrderByUUID(BaseModel):
    unit_name: str
    created_at: datetime
    receipt_printed_at: datetime | None
    number: str
    type: str
    price: int
    uuid: UUID


class CheatedOrder(BaseModel):
    created_at: datetime
    number: str


class CheatedOrders(BaseModel):
    unit_name: str
    phone_number: str
    orders: list[CheatedOrder]


class StockBalance(BaseModel):
    unit_id: int
    ingredient_name: str
    days_left: int
    stocks_count: float | int
    stocks_unit: str


class StockBalanceStatistics(BaseModel):
    error_unit_ids: list[int]
    units: list[StockBalance]
