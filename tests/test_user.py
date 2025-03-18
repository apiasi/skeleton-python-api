from pydantic import ValidationError
from app.models.user import User


def test_user_model():
    user = User(email="test@example.com", full_name="Test User")
    assert user.email == "test@example.com"
    assert user.full_name == "Test User"


def test_user_model_invalid_email():
    try:
        User(email="invalid-email", full_name="Test User")
    except ValidationError as e:
        assert "value is not a valid email address" in str(e)
