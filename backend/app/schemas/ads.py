from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime

class GenericSuccessResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None

# --- Schemas for /api/ads/center ---

class AdsCenterAccountRow(BaseModel):
    account_id: int
    account_name: str
    spend_today: int
    gmv_today: int
    roas_auto: Optional[float]
    roas_manual: Optional[float]
    roas_final: Optional[float]
    
    # Boros Logic
    boros_score: int
    boros_status: str # AMAN, WASPADA, BOROS
    boros_reason: Optional[str]
    
    # Audience Logic
    audience_threshold: int
    audience_gap_minutes: int
    audience_status: str # AMAN, HAMPIR_HABIS
    
    last_add_budget_at: Optional[str] # HH:MM:SS
    total_added_budget_today: int

# --- Upsert Requests ---

class SpendUpsertRequest(BaseModel):
    date: date
    account_id: int
    spend_amount: int
    spend_type: str = "general" # audience, live, general
    note: Optional[str] = None

class MetricsUpsertRequest(BaseModel):
    date: date
    account_id: int
    roas_manual: Optional[float]
    revenue_manual: Optional[int]
    note: Optional[str] = None

# --- Audience Settings ---

class AudienceSettingsUpsertRequest(BaseModel):
    account_id: int
    min_remaining_threshold: int
    min_gap_minutes: int
    active_start_time: str
    active_end_time: str
    max_daily_add_budget: Optional[int]
    is_enabled: bool

class AudienceAddBudgetRequest(BaseModel):
    date: date
    account_id: int
    added_amount: int
    remaining_before: Optional[int] = None

# --- Logs ---

class LogsSpendRow(BaseModel):
    id: int
    date: date
    account_name: str
    spend_amount: int
    spend_type: str
    note: Optional[str]
    created_by: Optional[str]
    created_at: datetime

class LogsAudienceRow(BaseModel):
    id: int
    date: date
    time: str
    account_name: str
    remaining_before: Optional[int]
    added_amount: int
    remaining_after: Optional[int]
    trigger_reason: str
    created_by: Optional[str]
    created_at: datetime

class LogsRoasRow(BaseModel):
    id: int
    date: date
    account_name: str
    roas_manual: float
    revenue_manual: Optional[int] = None
    note: Optional[str]
    created_by: Optional[str]
    created_at: datetime
    
class LogsRoasRowFixed(LogsRoasRow):
    # Redeclare to fix typo if any
    pass
