from django.conf import settings
from django.db import connection


def get_tenant_identifier() -> str:
    """Get name used to identify notification by tenant.
    Note that this is very specific to Timon needs.

    Returns:
        str: Tenant identifier
    """
    try:
        return connection.get_threadlocal().get_db_name()
    except Exception:
        return getattr(settings, 'WEB_NAME', '')
