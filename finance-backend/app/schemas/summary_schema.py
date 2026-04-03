"""
schemas/summary_schema.py
--------------------------
Response models for dashboard summary endpoints.
"""

from typing import List
from pydantic import BaseModel


class CategoryTotal(BaseModel):
    category:       str
    total:          float
    income_total:   float
    expense_total:  float
    count:          int


class MonthlyTrend(BaseModel):
    month:   str        # e.g. "2024-06"
    income:  float
    expense: float
    net:     float


class WeeklyTrend(BaseModel):
    week:    str        # e.g. "2024-W23"
    income:  float
    expense: float
    net:     float


class RecentRecord(BaseModel):
    id:       int
    amount:   float
    type:     str
    category: str
    date:     str
    notes:    str | None

    model_config = {"from_attributes": True}


class DashboardSummary(BaseModel):
    total_income:    float
    total_expense:   float
    net_balance:     float
    record_count:    int
    category_totals: List[CategoryTotal]
    monthly_trends:  List[MonthlyTrend]
    weekly_trends:   List[WeeklyTrend]
    recent_activity: List[RecentRecord]
