"""
services/summary_service.py
----------------------------
Aggregation logic for the dashboard summary APIs.
Single DB query fetches all records; Python handles all grouping
so the service stays database-agnostic (SQLite ↔ PostgreSQL).
"""

from collections import defaultdict
from typing import List
from sqlalchemy.orm import Session

from app.models.record_model import FinancialRecord
from app.schemas.summary_schema import (
    DashboardSummary, CategoryTotal,
    MonthlyTrend, WeeklyTrend, RecentRecord,
)


def get_dashboard_summary(db: Session) -> DashboardSummary:
    """
    Return the full dashboard in one pass over all records.

    Aggregates:
      - total_income / total_expense / net_balance
      - per-category breakdown (income + expense subtotals)
      - monthly trends  (YYYY-MM)
      - weekly  trends  (YYYY-Www)
      - recent activity (last 10 records by date)
    """
    rows = db.query(FinancialRecord).order_by(FinancialRecord.date.desc()).all()

    total_income  = 0.0
    total_expense = 0.0

    # category → {income, expense, count}
    cat_map: dict = defaultdict(lambda: {"income": 0.0, "expense": 0.0, "count": 0})
    # "YYYY-MM" → {income, expense}
    month_map: dict = defaultdict(lambda: {"income": 0.0, "expense": 0.0})
    # "YYYY-Www" → {income, expense}
    week_map: dict  = defaultdict(lambda: {"income": 0.0, "expense": 0.0})

    for row in rows:
        amt  = row.amount
        rtype = row.type
        cat  = row.category
        month_key = row.date.strftime("%Y-%m")
        week_key  = row.date.strftime("%Y-W%W")   # ISO week number

        if rtype == "income":
            total_income  += amt
        else:
            total_expense += amt

        cat_map[cat][rtype]   += amt
        cat_map[cat]["count"] += 1
        month_map[month_key][rtype] += amt
        week_map[week_key][rtype]   += amt

    # ── Category totals ───────────────────────────────────────────────────────
    category_totals = [
        CategoryTotal(
            category      = cat,
            total         = round(d["income"] - d["expense"], 2),
            income_total  = round(d["income"], 2),
            expense_total = round(d["expense"], 2),
            count         = d["count"],
        )
        for cat, d in sorted(cat_map.items())
    ]

    # ── Monthly trends ────────────────────────────────────────────────────────
    monthly_trends = [
        MonthlyTrend(
            month   = m,
            income  = round(d["income"], 2),
            expense = round(d["expense"], 2),
            net     = round(d["income"] - d["expense"], 2),
        )
        for m, d in sorted(month_map.items())
    ]

    # ── Weekly trends ─────────────────────────────────────────────────────────
    weekly_trends = [
        WeeklyTrend(
            week    = w,
            income  = round(d["income"], 2),
            expense = round(d["expense"], 2),
            net     = round(d["income"] - d["expense"], 2),
        )
        for w, d in sorted(week_map.items())
    ]

    # ── Recent activity (last 10) ─────────────────────────────────────────────
    recent_activity = [
        RecentRecord(
            id       = r.id,
            amount   = r.amount,
            type     = r.type,
            category = r.category,
            date     = r.date.strftime("%Y-%m-%d"),
            notes    = r.notes,
        )
        for r in rows[:10]
    ]

    return DashboardSummary(
        total_income    = round(total_income, 2),
        total_expense   = round(total_expense, 2),
        net_balance     = round(total_income - total_expense, 2),
        record_count    = len(rows),
        category_totals = category_totals,
        monthly_trends  = monthly_trends,
        weekly_trends   = weekly_trends,
        recent_activity = recent_activity,
    )


def get_recent_records(db: Session, limit: int = 10) -> List[RecentRecord]:
    """Return the most recent `limit` records sorted by date descending."""
    rows = (
        db.query(FinancialRecord)
        .order_by(FinancialRecord.date.desc())
        .limit(limit)
        .all()
    )
    return [
        RecentRecord(
            id       = r.id,
            amount   = r.amount,
            type     = r.type,
            category = r.category,
            date     = r.date.strftime("%Y-%m-%d"),
            notes    = r.notes,
        )
        for r in rows
    ]
