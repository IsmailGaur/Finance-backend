"""
routers/summary_routes.py
--------------------------
Dashboard summary endpoints – all restricted to Analyst + Admin.

GET /summary/            → full dashboard (all metrics)
GET /summary/income      → total income only
GET /summary/expense     → total expense only
GET /summary/balance     → net balance
GET /summary/categories  → category-wise breakdown
GET /summary/trends      → monthly income/expense trends
GET /summary/weekly      → weekly income/expense trends
GET /summary/recent      → most recent N records (activity feed)
"""

from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.role_checker import analyst_or_admin
from app.services import summary_service
from app.schemas.summary_schema import (
    DashboardSummary, CategoryTotal,
    MonthlyTrend, WeeklyTrend, RecentRecord,
)

router = APIRouter(prefix="/summary", tags=["Dashboard Summary"])


@router.get(
    "/",
    response_model=DashboardSummary,
    summary="Full dashboard summary  [Analyst + Admin]",
)
def full_summary(
    db: Session = Depends(get_db),
    _: object   = Depends(analyst_or_admin),
):
    """
    One-call endpoint returning every dashboard metric:
    totals, net balance, category breakdown, monthly trends,
    weekly trends, and recent activity feed.
    """
    return summary_service.get_dashboard_summary(db)


@router.get("/income", summary="Total income  [Analyst + Admin]")
def total_income(db: Session = Depends(get_db), _=Depends(analyst_or_admin)):
    data = summary_service.get_dashboard_summary(db)
    return {"total_income": data.total_income}


@router.get("/expense", summary="Total expense  [Analyst + Admin]")
def total_expense(db: Session = Depends(get_db), _=Depends(analyst_or_admin)):
    data = summary_service.get_dashboard_summary(db)
    return {"total_expense": data.total_expense}


@router.get("/balance", summary="Net balance  [Analyst + Admin]")
def net_balance(db: Session = Depends(get_db), _=Depends(analyst_or_admin)):
    data = summary_service.get_dashboard_summary(db)
    return {
        "total_income":  data.total_income,
        "total_expense": data.total_expense,
        "net_balance":   data.net_balance,
    }


@router.get(
    "/categories",
    response_model=List[CategoryTotal],
    summary="Category-wise totals  [Analyst + Admin]",
)
def category_totals(db: Session = Depends(get_db), _=Depends(analyst_or_admin)):
    """Returns income total, expense total and net per category."""
    return summary_service.get_dashboard_summary(db).category_totals


@router.get(
    "/trends",
    response_model=List[MonthlyTrend],
    summary="Monthly income/expense trends  [Analyst + Admin]",
)
def monthly_trends(db: Session = Depends(get_db), _=Depends(analyst_or_admin)):
    return summary_service.get_dashboard_summary(db).monthly_trends


@router.get(
    "/weekly",
    response_model=List[WeeklyTrend],
    summary="Weekly income/expense trends  [Analyst + Admin]",
)
def weekly_trends(db: Session = Depends(get_db), _=Depends(analyst_or_admin)):
    """Groups records by ISO calendar week (YYYY-Www)."""
    return summary_service.get_dashboard_summary(db).weekly_trends


@router.get(
    "/recent",
    response_model=List[RecentRecord],
    summary="Recent activity feed  [Analyst + Admin]",
)
def recent_activity(
    limit: int  = Query(10, ge=1, le=50, description="Number of recent records to return"),
    db: Session = Depends(get_db),
    _: object   = Depends(analyst_or_admin),
):
    """
    Returns the most recent financial records sorted newest-first.
    Useful for an activity feed widget on the dashboard.
    """
    return summary_service.get_recent_records(db, limit=limit)
