"""
This file (test_watchlist.py) contains the functional tests for the `watchlist` blueprint.
"""
import re


def test_get_add_watch_stock_page(test_client, log_in_default_user):
    """
    GIVEN a Flask application configured for testing and the default user logged in
    WHEN the '/watchlist/add_watch_stock' page is requested (GET)
    THEN check that the response is valid
    """
    response = test_client.get('/watchlist/add_watch_stock', follow_redirects=True)
    assert response.status_code == 200
    assert b'Flask Stock Portfolio App' in response.data
    assert b'Add Stock to Watchlist' in response.data
    assert b'Stock Symbol' in response.data
    assert b'Add' in response.data


def test_get_add_watch_stock_page_not_logged_in(test_client):
    """
    GIVEN a Flask application configured for testing without a user logged in
    WHEN the '/watchlist/add_watch_stock' page is requested (GET)
    THEN check that the user is redirected to the login page
    """
    response = test_client.get('/watchlist/add_watch_stock', follow_redirects=True)
    assert response.status_code == 200
    assert b'Flask Stock Portfolio App' in response.data
    assert b'Add Stock to Watchlist' not in response.data
    assert b'Please log in to access this page.' in response.data


def test_post_add_watch_stock_valid(test_client, log_in_default_user, mock_requests_get_success_overview):
    """
    GIVEN a Flask application configured for testing and the default user logged in
    WHEN the '/watchlist/add_watch_stock' page is posted to (POST)
    THEN check that a message is displayed to the user that the stock was added
    """
    response = test_client.post('/watchlist/add_watch_stock',
                                data={'stock_symbol': 'COST'},
                                follow_redirects=True)
    assert response.status_code == 200
    assert b'Watchlist' in response.data
    assert b'Stock Symbol' in response.data
    assert b'Added new stock (COST) to the watchlist!' in response.data


def test_post_add_watch_stock_not_logged_in(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/watchlist/add_watch_stock' page is posted to (POST)
    THEN check that the user is redirected to the login page
    """
    response = test_client.post('/watchlist/add_watch_stock',
                                data={'stock_symbol': 'COST'},
                                follow_redirects=True)
    assert response.status_code == 200
    assert b'Watchlist' not in response.data
    assert b'Added new stock (COST) to the watchlist!' not in response.data
    assert b'Please log in to access this page.' in response.data


def test_post_add_watch_stock_invalid_input(test_client, log_in_default_user):
    """
    GIVEN a Flask application configured for testing and the default user logged in
    WHEN the '/watchlist/add_watch_stock' page is posted to (POST) with invalid data
    THEN check that an error message is displayed
    """
    response = test_client.post('/watchlist/add_watch_stock',
                                data={'stock_symbol': 'I want to add more stocks!'},
                                follow_redirects=True)
    assert response.status_code == 200
    assert b'Add Stock to Watchlist' in response.data
    assert b'[Field must be between 1 and 10 characters long.]' in response.data
    assert b'Added new stock (COST) to the watchlist!' not in response.data


def test_get_watchlist_page(test_client, add_watch_stocks_for_default_user, mock_requests_get_success_overview):
    """
    GIVEN a Flask application configured for testing and the default user logged in
    WHEN the '/watchlist' page is requested (GET)
    THEN check that the response is valid
    """
    headers = [b'Stock Symbol', b'52-Week Low', b'Share Price', b'52-Week High', b'Market Cap',
               b'Dividend Per Share', b'P/E Ratio', b'PEG Ratio', b'Profit Margin', b'Price-to-Book Ratio']
    data = [b'COST', b'$262.68', b'$0.0', b'$388.07', b'160.3B', b'$2.8', b'37.15', b'3.93', b'25.03', b'5.23',
            b'MSFT', b'$262.68', b'$0.0', b'$388.07', b'160.3B', b'$2.8', b'37.15', b'3.93', b'25.03', b'5.23',
            b'QCOM', b'$262.68', b'$0.0', b'$388.07', b'160.3B', b'$2.8', b'37.15', b'3.93', b'25.03', b'5.23']

    response = test_client.get('/watchlist', follow_redirects=True)
    assert response.status_code == 200
    assert b'Flask Stock Portfolio App' in response.data
    assert b'Watchlist' in response.data
    for header in headers:
        assert header in response.data
    for element in data:
        assert element in response.data


def test_get_watchlist_page_not_logged_in(test_client):
    """
    GIVEN a Flask application configured for testing without a user logged in
    WHEN the '/watchlist' page is requested (GET)
    THEN check that the user is redirected to the login page
    """
    response = test_client.get('/watchlist', follow_redirects=True)
    assert response.status_code == 200
    assert b'Flask Stock Portfolio App' in response.data
    assert b'Watchlist' not in response.data
    assert b'Please log in to access this page.' in response.data


def test_delete_watchlist_stock_valid(test_client, log_in_default_user,
                                      add_watch_stocks_for_default_user, mock_requests_get_success_overview):
    """
    GIVEN a Flask application configured for testing, with the default user logged in
          and the default set of watchstocks in the database
    WHEN the '/watchlist/3/delete' page is retrieved (GET)
    THEN check that the response is valid and a success message is displayed
    """
    response = test_client.get('/watchlist/3/delete', follow_redirects=True)
    assert response.status_code == 200
    assert re.search(r"Stock \(.*[A-Z]{4}.*was deleted!", str(response.data))
    assert b'Watchlist' in response.data


def test_delete_watchlist_stock_not_owning_stock(test_client, log_in_second_user,
                                                 add_watch_stocks_for_default_user,
                                                 mock_requests_get_success_overview):
    """
    GIVEN a Flask application configured for testing, with the default user logged in
          and the default set of watchstocks in the database
    WHEN the '/watchlist/2/delete' page is retrieved (GET)
    THEN check that an error message is displayed
    """
    response = test_client.get('/watchlist/2/delete', follow_redirects=True)
    assert response.status_code == 403
    assert not re.search(r"Stock \(.*[A-Z]{4}.*was deleted!", str(response.data))


def test_delete_watchlist_stock_not_logged_in(test_client):
    """
    GIVEN a Flask application configured for testing without a user logged in
    WHEN the '/watchlist/1/delete' page is retrieved (GET)
    THEN check that an error message is displayed
    """
    response = test_client.get('/watchlist/1/delete', follow_redirects=True)
    assert response.status_code == 200
    assert not re.search(r"Stock \(.*[A-Z]{4}.*was deleted!", str(response.data))
    assert b'Please log in to access this page.' in response.data


def test_delete_stock_invalid_stock(test_client, log_in_default_user):
    """
    GIVEN a Flask application configured for testing with the default user logged in
    WHEN the '/watchlist/7329/delete' page is retrieved (GET)
    THEN check that an error message is displayed
    """
    response = test_client.get('/watchlist/7329/delete', follow_redirects=True)
    assert response.status_code == 404
    assert not re.search(r"Stock \(.*[A-Z]{4}.*was deleted!", str(response.data))


def test_get_stock_analysis_guide_page(test_client, log_in_default_user):
    """
    GIVEN a Flask application configured for testing with the default user logged in
    WHEN the '/stock_analysis_guide' page is retrieved (GET)
    THEN check that the response is valid
    """
    response = test_client.get('/stock_analysis_guide', follow_redirects=True)
    assert response.status_code == 200
    assert b'Stock Analysis Guide' in response.data
