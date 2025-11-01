from django import template
from django.utils import timezone
from datetime import timedelta

register = template.Library()

@register.filter
def format_salary(value):
    # TODO: add millions
    """convert salary to thousand format (1k)"""
    try:
        value = int(value)
        if value >= 1000:
            return f"{value // 1000}k"
        else:
            return str(value)
    except (ValueError, TypeError):
        return value

@register.filter
def time_ago(value):
    """
    convert a datetime to a short format (1h ago)
    """
    if not value:
        return ''
    
    now = timezone.now()
    diff = now - value
    
    seconds = diff.total_seconds()
    
    if seconds < 60:
        return 'just now'
    elif seconds < 3600:  # less than 1 hour
        minutes = int(seconds / 60)
        return f'{minutes}m ago'
    elif seconds < 86400:  # less than 1 day
        hours = int(seconds / 3600)
        return f'{hours}h ago'
    elif seconds < 604800:  # less than 1 week
        days = int(seconds / 86400)
        return f'{days}d ago'
    elif seconds < 2592000:  # less than 30 days
        weeks = int(seconds / 604800)
        return f'{weeks}w ago'
    elif seconds < 31536000:  # less than 1 year
        months = int(seconds / 2592000)
        return f'{months}mo ago'
    else:
        years = int(seconds / 31536000)
        return f'{years}y ago'