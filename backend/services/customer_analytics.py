"""Customer churn and lifetime-value summaries from mill orders (no ML)."""

from datetime import datetime, timedelta

from sqlalchemy import func

from models.sales import Customer, SalesOrder
from services.tenant_scope import tq


def _days_since(when, now):
    if not when:
        return None
    return max(0, (now - when).days)


def recency_churn_score(last_order_date, is_active, now):
    """Heuristic from last order date — not a trained model."""
    if not is_active:
        return 0.85
    if not last_order_date:
        return 0.8
    days = _days_since(last_order_date, now)
    if days > 180:
        return 0.9
    if days > 90:
        return 0.7
    if days > 60:
        return 0.4
    return 0.1


def churn_from_orders(risk_threshold=0.7):
    now = datetime.utcnow()
    customers = tq(Customer).all()
    high = []
    for customer in customers:
        score = recency_churn_score(customer.last_order_date, customer.is_active, now)
        if score < risk_threshold:
            continue
        high.append({
            'customer_id': customer.id,
            'name': customer.name,
            'churn_probability': score,
            'last_order_date': (
                customer.last_order_date.isoformat() if customer.last_order_date else None
            ),
            'reason': (
                'inactive' if not customer.is_active
                else ('no_orders' if not customer.last_order_date else 'stale_orders')
            ),
        })
    return {
        'high_risk_customers': high,
        'churn_prediction': {
            'at_risk_count': len(high),
            'customer_count': len(customers),
            'method': 'order_recency',
        },
        'retention_strategies': [],
        'method': 'order_recency',
    }


def _order_total_between(start, end):
    total = (
        tq(SalesOrder)
        .filter(SalesOrder.created_at >= start, SalesOrder.created_at < end)
        .with_entities(func.coalesce(func.sum(SalesOrder.total_amount), 0.0))
        .scalar()
    )
    return float(total or 0)


def lifetime_value_from_orders():
    now = datetime.utcnow()
    recent_start = now - timedelta(days=90)
    previous_start = now - timedelta(days=180)
    customers = tq(Customer).all()
    values = [float(customer.total_order_value or 0) for customer in customers]
    average = (sum(values) / len(values)) if values else 0.0
    recent = _order_total_between(recent_start, now)
    previous = _order_total_between(previous_start, recent_start)
    if previous:
        growth_rate = ((recent - previous) / previous) * 100
    else:
        growth_rate = 100.0 if recent else 0.0
    return {
        'average_ltv': round(average, 2),
        'ltv_trends': {'growth_rate': round(growth_rate, 1)},
        'clv_analysis': {
            'customer_count': len(customers),
            'total_order_value': round(sum(values), 2),
            'method': 'order_totals',
        },
        'value_optimization': [],
        'method': 'order_totals',
    }
