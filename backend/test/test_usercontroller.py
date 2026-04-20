"""Unit tests for UserController.get_user_by_email()."""

from unittest.mock import Mock
import pytest
from src.controllers.usercontroller import UserController

def make_controller():
    """Create a UserController with a mocked DAO."""
    dao = Mock()
    return UserController(dao), dao

def test_get_user_by_email_raises_value_error_for_invalid_email():
    """Invalid email without @ should raise ValueError."""
    controller, dao = make_controller()

    with pytest.raises(ValueError):
        controller.get_user_by_email("invalid-email")

    dao.find.assert_not_called()

def test_get_user_by_email_returns_user_when_one_match_exists():
    """A valid email with one DAO match should return that user."""
    controller, dao = make_controller()
    user = {"email": "test@example.com", "name": "Melissa"}
    dao.find.return_value = [user]

    result = controller.get_user_by_email("test@example.com")

    assert result == user
    dao.find.assert_called_once_with({"email": "test@example.com"})

def test_get_user_by_email_returns_first_user_and_prints_warning_when_multiple_matches_exist(capsys):
    """Multiple matches should return the first user and print a warning."""
    controller, dao = make_controller()
    user1 = {"email": "test@example.com", "name": "Melissa"}
    user2 = {"email": "test@example.com", "name": "Other"}
    dao.find.return_value = [user1, user2]

    result = controller.get_user_by_email("test@example.com")
    captured = capsys.readouterr()

    assert result == user1
    assert "more than one user found with mail test@example.com" in captured.out
    dao.find.assert_called_once_with({"email": "test@example.com"})

def test_get_user_by_email_returns_none_when_no_user_exists():
    """No DAO match should return None according to the specification."""
    controller, dao = make_controller()
    dao.find.return_value = []

    result = controller.get_user_by_email("test@example.com")

    assert result is None
    dao.find.assert_called_once_with({"email": "test@example.com"})

def test_get_user_by_email_propagates_exception_from_dao():
    """DAO exceptionss should be propagated by the method."""
    controller, dao = make_controller()
    dao.find.side_effect = Exception("database failure")

    with pytest.raises(Exception, match="database failure"):
        controller.get_user_by_email("test@example.com")

    dao.find.assert_called_once_with({"email": "test@example.com"})

def test_get_user_by_email_rejects_email_without_domain_and_host():
    """Email missing domain host should raise ValueError per the docstring."""
    controller, dao = make_controller()
    dao.find.return_value = [{"email": "a@b"}]

    with pytest.raises(ValueError):
        controller.get_user_by_email("a@b")

    dao.find.assert_not_called()