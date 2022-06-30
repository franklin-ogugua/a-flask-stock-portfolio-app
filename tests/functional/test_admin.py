"""
This file (test_admin.py) contains the functional tests for the `admin` blueprint.
"""
import re


def test_cli_create_admin_user(cli_test_runner):
    """
    GIVEN a Flask CLI test runner
    WHEN the 'flask admin create_admin_user' command is processed
    THEN check that a new admin user is created
    """
    result = cli_test_runner.invoke(args=['admin', 'create_admin_user',
                                          'patrick_admin2@email.com',
                                          'FlaskIsMyFavorite567'])
    assert 'Created new admin user (patrick_admin2@email.com)!' in result.output


def test_admin_view_users_valid(test_client_admin, log_in_admin_user):
    """
    GIVEN a Flask application configured for testing with the admin user logged in
          and the default set of users in the database
    WHEN the '/admin/users' page is requested (GET)
    THEN check the response is valid and all expected users are listed
    """
    expected_users = [b'patrick_admin@gmail.com',  # Admin
                      b'user1@gmail.com',
                      b'user2@gmail.com',
                      b'user3@gmail.com',
                      b'user4@gmail.com']
    expected_actions = [b'Delete',
                        b'Confirm Email',
                        b'Change Email',
                        b'Change Password']

    response = test_client_admin.get('/admin/users', follow_redirects=True)
    assert response.status_code == 200
    assert b'List of Users' in response.data
    for expected_user in expected_users:
        assert expected_user in response.data
    assert b'ID' in response.data
    assert b'Email' in response.data
    assert b'Registration Date' in response.data
    assert b'Email Confirmation Date' in response.data
    assert b'User Type' in response.data
    assert b'# of Stocks in Portfolio' in response.data
    assert b'# of Stocks in Watchlist' in response.data
    assert b'Actions' in response.data
    for expected_action in expected_actions:
        assert expected_action in response.data


def test_admin_views_non_admin_user(test_client_admin, log_in_user1):
    """
    GIVEN a Flask application configured for testing with a non-admin user logged in
    WHEN the specified routes are requested (GET) or posted to (POST)
    THEN check that a 403 error is returned
    """
    routes_get = ['/admin/users',
                  '/admin/users/4/delete',
                  '/admin/users/5/confirm_email',
                  '/admin/users/5/unconfirm_email',
                  '/admin/users/1/change_password',
                  '/admin/users/1/change_email']

    routes_post = [{'url': '/admin/users/4/change_password', 'data': {'password': 'FlaskIsGreat101'}},
                   {'url': '/admin/users/5/change_email', 'data': {'email': 'user104@gmail.com'}}]

    for route in routes_get:
        response = test_client_admin.get(route, follow_redirects=True)
        assert response.status_code == 403
        assert b'List of Users' not in response.data

    for route in routes_post:
        response = test_client_admin.post(route['url'],
                                          data=route['data'],
                                          follow_redirects=True)
        assert response.status_code == 403
        assert b'List of Users' not in response.data


def test_admin_view_users_not_logged_in(test_client_admin):
    """
    GIVEN a Flask application configured for testing without a user logged in
    WHEN the specified routes are requested (GET) or posted to (POST)
    THEN check that an error message is returned
    """
    routes_get = ['/admin/users',
                  '/admin/users/4/delete',
                  '/admin/users/5/confirm_email',
                  '/admin/users/5/unconfirm_email',
                  '/admin/users/1/change_password',
                  '/admin/users/1/change_email']

    routes_post = [{'url': '/admin/users/4/change_password', 'data': {'password': 'FlaskIsGreat101'}},
                   {'url': '/admin/users/5/change_email', 'data': {'email': 'user104@gmail.com'}}]

    for route in routes_get:
        response = test_client_admin.get(route, follow_redirects=True)
        assert response.status_code == 200
        assert b'List of Users' not in response.data
        assert b'Please log in to access this page.' in response.data

    for route in routes_post:
        response = test_client_admin.post(route['url'],
                                          data=route['data'],
                                          follow_redirects=True)
        assert response.status_code == 200
        assert b'List of Users' not in response.data
        assert b'Please log in to access this page.' in response.data


def test_admin_confirm_email_invalid_user_id(test_client_admin, log_in_admin_user):
    """
    GIVEN a Flask application configured for testing with the admin user logged in
          and the default set of users in the database
    WHEN the specified routes are requested (GET) or posted to (POST)
    THEN check that a 404 error is returned
    """
    routes_get = ['/admin/users/4789/delete',
                  '/admin/users/4789/confirm_email',
                  '/admin/users/4789/unconfirm_email']

    routes_post = [{'url': '/admin/users/6729/change_password',
                    'data': {'password': 'FlaskIsGreat101'}},
                   {'url': '/admin/users/7612/change_email',
                    'data': {'email': 'user104@gmail.com'}}]

    for route in routes_get:
        response = test_client_admin.get(route, follow_redirects=True)
        assert response.status_code == 404
        assert b'List of Users' not in response.data

    for route in routes_post:
        response = test_client_admin.post(route['url'],
                                          data=route['data'],
                                          follow_redirects=True)
        assert response.status_code == 404
        assert b'List of Users' not in response.data


def test_admin_navigation_links(test_client_admin, log_in_admin_user):
    """
    GIVEN a Flask application configured for testing with the admin user logged in
          and the default set of users in the database
    WHEN the '/' page is requested (GET)
    THEN check the response is valid and the 'Admin' link is in the navigation bar
    """
    response = test_client_admin.get('/', follow_redirects=True)
    assert response.status_code == 200
    assert b'Welcome to the' in response.data
    assert b'Flask Stock Portfolio App!' in response.data
    assert b'Portfolio' in response.data
    assert b'Watchlist' in response.data
    assert b'Profile' in response.data
    assert b'Admin' in response.data
    assert b'Logout' in response.data


def test_admin_delete_user_valid(test_client_admin, log_in_admin_user):
    """
    GIVEN a Flask application configured for testing with the admin user logged in
          and the default set of users in the database
    WHEN the '/admin/users/2/delete' page is requested (GET)
    THEN check the response is valid and a success message is displayed
    """
    response = test_client_admin.get('/admin/users/3/delete', follow_redirects=True)
    assert response.status_code == 200
    assert re.search(r"User \(.*\) was deleted!", str(response.data))
    assert b'List of Users' in response.data


def test_admin_delete_admin_user(test_client_admin, log_in_admin_user):
    """
    GIVEN a Flask application configured for testing with the admin user logged in
          and the default set of users in the database
    WHEN the '/admin/users/1/delete' page is requested (GET)
    THEN check that an error message is displayed about not being able to delete admin users
    """
    response = test_client_admin.get('/admin/users/1/delete', follow_redirects=True)
    assert response.status_code == 200
    assert b'Error! Admin users cannot be deleted!'
    assert b'List of Users' in response.data


def test_admin_confirm_email_valid(test_client_admin, log_in_admin_user):
    """
    GIVEN a Flask application configured for testing with the admin user logged in
          and the default set of users in the database
    WHEN the '/admin/users/4/confirm_email' page is requested (GET)
    THEN check the response is valid and a success message is displayed
    """
    response = test_client_admin.get('/admin/users/4/confirm_email', follow_redirects=True)
    assert response.status_code == 200
    assert re.search(r"User.*email address \(.*\) was confirmed!", str(response.data))
    assert b'List of Users' in response.data


def test_admin_unconfirm_email_valid(test_client_admin, log_in_admin_user):
    """
    GIVEN a Flask application configured for testing with the admin user logged in
          and the default set of users in the database
    WHEN the '/admin/users/4/unconfirm_email' page is requested (GET)
    THEN check the response is valid and a success message is displayed
    """
    response = test_client_admin.get('/admin/users/4/unconfirm_email', follow_redirects=True)
    assert response.status_code == 200
    assert re.search(r"User.*email address \(.*\) was un-confirmed!", str(response.data))
    assert b'List of Users' in response.data


def test_admin_get_change_password_page_valid(test_client_admin, log_in_admin_user):
    """
    GIVEN a Flask application configured for testing with the admin user logged in
          and the default set of users in the database
    WHEN the '/admin/users/1/change_password' page is requested (GET)
    THEN check the response is valid
    """
    response = test_client_admin.get('/admin/users/1/change_password', follow_redirects=True)
    assert response.status_code == 200
    assert b'Change Password' in response.data
    assert b'New Password' in response.data
    assert b'Submit' in response.data


def test_admin_post_change_password_valid(test_client_admin, log_in_admin_user):
    """
    GIVEN a Flask application configured for testing with the admin user logged in
          and the default set of users in the database
    WHEN the '/admin/users/4/change_password' page is posted to (POST})
    THEN check the response is valid
    """
    response = test_client_admin.post('/admin/users/4/change_password',
                                      data={'password': 'FlaskIsGreat101'},
                                      follow_redirects=True)
    assert response.status_code == 200
    assert re.search(r"User.* password \(.*\) was updated!", str(response.data))
    assert b'List of Users' in response.data


def test_admin_get_change_email_page_valid(test_client_admin, log_in_admin_user):
    """
    GIVEN a Flask application configured for testing with the admin user logged in
          and the default set of users in the database
    WHEN the '/admin/users/5/change_email' page is requested (GET)
    THEN check the response is valid
    """
    response = test_client_admin.get('/admin/users/1/change_email', follow_redirects=True)
    assert response.status_code == 200
    assert b'Change Email' in response.data
    assert b'New Email' in response.data
    assert b'Submit' in response.data


def test_admin_post_change_email_valid(test_client_admin, log_in_admin_user):
    """
    GIVEN a Flask application configured for testing with the admin user logged in
          and the default set of users in the database
    WHEN the '/admin/users/5/change_email' page is posted to (POST})
    THEN check the response is valid
    """
    response = test_client_admin.post('/admin/users/5/change_email',
                                      data={'email': 'user104@gmail.com'},
                                      follow_redirects=True)
    assert response.status_code == 200
    assert re.search(r"User.* email \(.*\) was updated!", str(response.data))
    assert b'List of Users' in response.data
