from django import template
from datetime import date

register = template.Library()


@register.filter
def overdue_days(due_date):
    if not due_date:
        return 0
    delta = date.today() - due_date
    return max(0, delta.days)
