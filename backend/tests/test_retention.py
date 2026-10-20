import pytest

from app.services.retention import delete_expired_logs


def test_retention_rejects_invalid_period_before_database_work():
    with pytest.raises(ValueError):
        delete_expired_logs(None, 0)
