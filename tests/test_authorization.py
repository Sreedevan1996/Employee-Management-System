def test_anonymous_user_is_redirected_to_login_when_accessing_admin_dashboard(client):
    response = client.get("/admin/dashboard")

    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]


def test_employee_cannot_access_admin_dashboard(
    client,
    employee_user,
    login_as,
):
    login_as(employee_user["username"], employee_user["password"])

    response = client.get("/admin/dashboard")

    assert response.status_code == 403


def test_admin_cannot_access_employee_profile_dashboard(
    client,
    admin_user,
    login_as,
):
    login_as(admin_user["username"], admin_user["password"])

    response = client.get("/profile/dashboard")

    assert response.status_code == 403


def test_admin_can_access_employee_management_pages(
    client,
    admin_user,
    login_as,
):
    login_as(admin_user["username"], admin_user["password"])

    response = client.get("/employees/")

    assert response.status_code == 200


def test_employee_can_access_own_profile_dashboard(
    client,
    employee_user,
    employee_record,
    login_as,
):
    login_as(employee_user["username"], employee_user["password"])

    response = client.get("/profile/dashboard")

    assert response.status_code == 200