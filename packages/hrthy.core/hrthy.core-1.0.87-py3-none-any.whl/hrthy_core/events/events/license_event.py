from datetime import datetime
from enum import Enum
from uuid import UUID

from hrthy_core.events.events.base_event import BaseEvent, BasePayload, CompanyBasePayload


class LicensePoolType(Enum):
    TRIAL = 'trial'
    REGULAR = 'regular'


class LicensePoolCreatedPayload(CompanyBasePayload):
    active: bool
    pool_type: LicensePoolType
    total_licenses: int
    consumed_licenses: int
    available_licenses: int
    start_date: datetime
    end_date: datetime


class LicensePoolUpdatedPayload(LicensePoolCreatedPayload):
    pass


class LicensePoolDeletedPayload(CompanyBasePayload):
    pass


class LicenseConsumedPayload(BasePayload):
    company_id: UUID
    license_pool_id: UUID
    candidate_id: UUID
    candidate_first_name: str = None
    candidate_last_name: str = None
    candidate_email: str
    consumed_date: datetime


class LicensePoolCreatedEvent(BaseEvent):
    type = 'LicensePoolCreatedEvent'
    payload: LicensePoolCreatedPayload


class LicensePoolUpdatedEvent(BaseEvent):
    type = 'LicensePoolUpdatedEvent'
    payload: LicensePoolUpdatedPayload


class LicensePoolDeletedEvent(BaseEvent):
    type = 'LicensePoolDeletedEvent'
    payload: LicensePoolDeletedPayload


class LicenseConsumedEvent(BaseEvent):
    type = 'LicenseConsumedEvent'
    payload: LicenseConsumedPayload
