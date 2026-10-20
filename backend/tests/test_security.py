import jwt

from app.config import settings
from app.db.models import User
from app.security import create_access_token, password_hash


def test_password_hash_is_not_plaintext_and_verifies():
    hashed = password_hash.hash("test-password")
    assert hashed != "test-password"
    assert password_hash.verify("test-password", hashed)
    assert not password_hash.verify("wrong-password", hashed)


def test_access_token_contains_identity_and_tenant_claims():
    user = User(id="11111111-1111-1111-1111-111111111111", tenant_id="22222222-2222-2222-2222-222222222222", email="test@example.local", password_hash="not-used", role="viewer")
    claims = jwt.decode(create_access_token(user), settings.jwt_secret, algorithms=["HS256"])
    assert claims["sub"] == str(user.id)
    assert claims["tenant_id"] == str(user.tenant_id)
    assert claims["role"] == "viewer"
