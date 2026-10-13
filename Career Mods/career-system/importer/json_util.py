import datetime


def clean(obj):
    """Excel-Werte JSON-tauglich machen."""
    if isinstance(obj, dict):
        return {str(k): clean(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [clean(v) for v in obj]
    if isinstance(obj, (datetime.date, datetime.datetime)):
        return obj.isoformat()
    if isinstance(obj, float) and obj.is_integer():
        return int(obj)
    return obj
