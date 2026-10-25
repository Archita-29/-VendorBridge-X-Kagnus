
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.routers.vendors import require_roles


def make_user(role: str):
    return SimpleNamespace(role=role)


@pytest.mark.parametrize(
    "role",
    ["admin", "procurement_officer", "manager"],
)
def test_authorized_roles_can_view_vendors(role):
    check_role = require_roles(
        "admin", "procurement_officer", "manager"
    )

    user = make_user(role)

    assert check_role(current_user=user) is user


def test_vendor_role_cannot_view_vendor_directory():
    check_role = require_roles(
        "admin", "procurement_officer", "manager"
    )

    with pytest.raises(HTTPException) as exc:
        check_role(current_user=make_user("vendor"))

    assert exc.value.status_code == 403


def test_manager_cannot_use_procurement_only_permissions():
    check_role = require_roles("admin", "procurement_officer")

    with pytest.raises(HTTPException) as exc:
        check_role(current_user=make_user("manager"))

    assert exc.value.status_code == 403
