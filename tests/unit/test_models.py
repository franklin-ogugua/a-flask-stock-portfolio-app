"""
This file (test_models.py) contains the unit tests for the models.py file.
"""
from datetime import datetime
from freezegun import freeze_time


def test_new_stock(new_stock):
    """
    GIVEN a Stock model
    WHEN a new Stock object is created
    THEN check the symbol, number of shares, purchase price, user ID, and purchase date fields are defined correctly
    """
    assert new_stock.stock_symbol == 'AAPL'
    assert new_stock.number_of_shares == 16
    assert new_stock.purchase_price == 40678
    assert new_stock.user_id == 17
    assert new_stock.purchase_date.year == 2020
    assert new_stock.purchase_date.month == 7
    assert new_stock.purchase_date.day == 18


def test_new_user(new_user):
    """
    GIVEN a User model
    WHEN a new User object is created
    THEN check the email is valid and hashed password does not equal the password provided
    """
    assert new_user.email == 'patrick@email.com'
    assert new_user.password_hashed != 'FlaskIsAwesome123'
    assert new_user.user_type == 'User'
    assert not new_user.is_admin()
    assert not new_user.email_confirmed
    assert new_user.email_confirmed_on is None


def test_set_password(new_user):
    """
    GIVEN a User model
    WHEN the user's password is changed
    THEN check the password has been changed
    """
    new_user.set_password('FlaskIsStillAwesome456')
    assert new_user.email == 'patrick@email.com'
    assert new_user.password_hashed != 'FlaskIsStillAwesome456'
    assert new_user.is_password_correct('FlaskIsStillAwesome456')


def test_confirm_email_address(new_user):
    """
    GIVEN a User model
    WHEN the user's email address is confirmed
    THEN check that the email address is confirmed
    """
    assert not new_user.email_confirmed
    assert new_user.email_confirmed_on is None
    new_user.confirm_email_address()
    assert new_user.email_confirmed
    assert new_user.email_confirmed_on.date() == datetime.now().date()


def test_unconfirm_email_address(new_user):
    """
    GIVEN a User model with their email address confirmed
    WHEN the user's email address is un-confirmed
    THEN check that the email address is un-confirmed
    """
    new_user.confirm_email_address()
    assert new_user.email_confirmed
    assert new_user.email_confirmed_on.date() == datetime.now().date()
    new_user.unconfirm_email_address()
    assert not new_user.email_confirmed
    assert new_user.email_confirmed_on is None


def test_get_stock_data_success(new_stock, mock_requests_get_success_daily):
    """
    GIVEN a Flask application configured for testing and a monkeypatched version of requests.get()
    WHEN the HTTP response is set to successful
    THEN check that the stock data is updated
    """
    new_stock.get_stock_data()
    assert new_stock.stock_symbol == 'AAPL'
    assert new_stock.number_of_shares == 16
    assert new_stock.purchase_price == 40678  # $406.78 -> integer
    assert new_stock.purchase_date.date() == datetime(2020, 7, 18).date()
    assert new_stock.current_price == 14834  # $148.34 -> integer
    assert new_stock.current_price_date.date() == datetime.now().date()
    assert new_stock.position_value == (14834*16)


def test_get_stock_data_api_rate_limit_exceeded(new_stock, mock_requests_get_api_rate_limit_exceeded):
    """
    GIVEN a Flask application configured for testing and a monkeypatched version of requests.get()
    WHEN the HTTP response is set to successful but the API rate limit is exceeded
    THEN check that the stock data is not updated
    """
    new_stock.get_stock_data()
    assert new_stock.stock_symbol == 'AAPL'
    assert new_stock.number_of_shares == 16
    assert new_stock.purchase_price == 40678  # $406.78 -> integer
    assert new_stock.purchase_date.date() == datetime(2020, 7, 18).date()
    assert new_stock.current_price == 0
    assert new_stock.current_price_date is None
    assert new_stock.position_value == 0


def test_get_stock_data_failure(new_stock, mock_requests_get_failure):
    """
    GIVEN a Flask application configured for testing and a monkeypatched version of requests.get()
    WHEN the HTTP response is set to failed
    THEN check that the stock data is not updated
    """
    new_stock.get_stock_data()
    assert new_stock.stock_symbol == 'AAPL'
    assert new_stock.number_of_shares == 16
    assert new_stock.purchase_price == 40678  # $406.78 -> integer
    assert new_stock.purchase_date.date() == datetime(2020, 7, 18).date()
    assert new_stock.current_price == 0
    assert new_stock.current_price_date is None
    assert new_stock.position_value == 0


def test_get_stock_data_success_two_calls(new_stock, mock_requests_get_success_daily):
    """
    GIVEN a Flask application configured for testing and a monkeypatched version of requests.get()
    WHEN the HTTP response is set to successful
    THEN check that the stock data is updated
    """
    assert new_stock.stock_symbol == 'AAPL'
    assert new_stock.current_price == 0
    assert new_stock.current_price_date is None
    assert new_stock.position_value == 0
    new_stock.get_stock_data()
    assert new_stock.current_price == 14834  # $148.34 -> integer
    assert new_stock.current_price_date.date() == datetime.now().date()
    assert new_stock.position_value == (14834*16)
    new_stock.get_stock_data()
    assert new_stock.current_price == 14834  # $148.34 -> integer
    assert new_stock.current_price_date.date() == datetime.now().date()
    assert new_stock.position_value == (14834*16)


@freeze_time('2020-07-28')
def test_get_weekly_stock_data_success(new_stock, mock_requests_get_success_weekly):
    """
    GIVEN a Flask application configured for testing and a monkeypatched version of requests.get()
    WHEN the HTTP response is set to successful
    THEN check the HTTP response
    """
    title, labels, values = new_stock.get_weekly_stock_data()
    assert title == 'Weekly Prices (AAPL)'
    assert len(labels) == 3
    assert labels[0].date() == datetime(2020, 6, 11).date()
    assert labels[1].date() == datetime(2020, 7, 17).date()
    assert labels[2].date() == datetime(2020, 7, 24).date()
    assert len(values) == 3
    assert values[0] == '354.3400'
    assert values[1] == '362.7600'
    assert values[2] == '379.2400'
    assert datetime.now() == datetime(2020, 7, 28)


def test_get_weekly_stock_data_failure(new_stock, mock_requests_get_failure):
    """
    GIVEN a Flask application configured for testing and a monkeypatched version of requests.get()
    WHEN the HTTP response is set to failed
    THEN check the HTTP response
    """
    title, labels, values = new_stock.get_weekly_stock_data()
    assert title == 'Stock chart is unavailable.'
    assert len(labels) == 0
    assert len(values) == 0


def test_new_admin_user(new_admin_user):
    """
    GIVEN a User model
    WHEN a new User object is created with admin privileges
    THEN check the email is valid, the hashed password is valid, and the type is Admin
    """
    assert new_admin_user.email == 'patrick_admin@email.com'
    assert new_admin_user.password_hashed != 'FlaskIsTheBest987'
    assert new_admin_user.is_password_correct('FlaskIsTheBest987')
    assert new_admin_user.user_type == 'Admin'
    assert new_admin_user.is_admin()


def test_new_watchstock(new_watch_stock):
    """
    GIVEN a WatchStock model
    WHEN a new WatchStock object is created
    THEN check that the stock symbol is valid and all other fields are empty
    """
    assert new_watch_stock.stock_symbol == 'COST'
    assert new_watch_stock.company_name is None
    assert new_watch_stock.current_share_price == 0
    assert new_watch_stock.current_share_price_date is None
    assert new_watch_stock.fiftytwo_week_low == 0
    assert new_watch_stock.fiftytwo_week_high == 0
    assert new_watch_stock.market_cap is None
    assert new_watch_stock.dividend_per_share == 0
    assert new_watch_stock.pe_ratio == 0
    assert new_watch_stock.peg_ratio == 0
    assert new_watch_stock.profit_margin == 0
    assert new_watch_stock.beta == 0
    assert new_watch_stock.stock_data_date is None
    assert new_watch_stock.user_id == 23


def test_get_watchstock_current_share_price_success(new_watch_stock, mock_requests_get_success_daily):
    """
    GIVEN a monkeypatched (successful response) version of requests.get()
    WHEN the current share price is retrieved
    THEN check that the stock price returned is valid
    """
    new_watch_stock.retrieve_current_share_price()
    assert new_watch_stock.company_name is None
    assert new_watch_stock.current_share_price == 14834
    assert new_watch_stock.current_share_price_date.date() == datetime.now().date()


def test_get_watchstock_current_share_price_api_rate_limit_exceeded(new_watch_stock, mock_requests_get_api_rate_limit_exceeded):
    """
    GIVEN a monkeypatched (API rate limit exceeded) version of requests.get()
    WHEN the current share price is retrieved
    THEN check that the stock price returned is zero
    """
    new_watch_stock.retrieve_current_share_price()
    assert new_watch_stock.company_name is None
    assert new_watch_stock.current_share_price == 0
    assert new_watch_stock.current_share_price_date is None


def test_get_watchstock_current_share_price_failure(new_watch_stock, mock_requests_get_failure):
    """
    GIVEN a monkeypatched (failure) version of requests.get()
    WHEN the current share price is retrieved
    THEN check that the stock price returned is zero
    """
    new_watch_stock.retrieve_current_share_price()
    assert new_watch_stock.company_name is None
    assert new_watch_stock.current_share_price == 0
    assert new_watch_stock.current_share_price_date is None


def test_get_watchstock_data_success(new_watch_stock, mock_requests_get_success_overview):
    """
    GIVEN a monkeypatched (successful response) version of requests.get()
    WHEN the analysis data for the WatchStock object is retrieved
    THEN check that the analysis data returned is valid
    """
    new_watch_stock.retrieve_stock_analysis_data()
    assert new_watch_stock.stock_symbol == 'COST'
    assert new_watch_stock.company_name == 'Costco Wholesale Corporation'
    assert new_watch_stock.current_share_price == 0
    assert new_watch_stock.get_current_share_price() == 0
    assert new_watch_stock.current_share_price_date is None
    assert new_watch_stock.fiftytwo_week_low == 26268
    assert new_watch_stock.get_fiftytwo_week_low() == 262.68
    assert new_watch_stock.fiftytwo_week_high == 38807
    assert new_watch_stock.get_fiftytwo_week_high() == 388.07
    assert new_watch_stock.market_cap == '160300990464'
    assert new_watch_stock.get_market_cap() == '160.3B'
    assert new_watch_stock.dividend_per_share == 280
    assert new_watch_stock.get_dividend_per_share() == 2.8
    assert new_watch_stock.pe_ratio == 3715
    assert new_watch_stock.get_pe_ratio() == 37.15
    assert new_watch_stock.peg_ratio == 393
    assert new_watch_stock.get_peg_ratio() == 3.93
    assert new_watch_stock.profit_margin == 2503
    assert new_watch_stock.get_profit_margin() == 25.03
    assert new_watch_stock.beta == 67
    assert new_watch_stock.get_beta() == 0.67
    assert new_watch_stock.price_to_book_ratio == 523
    assert new_watch_stock.get_price_to_book_ratio() == 5.23
    assert new_watch_stock.stock_data_date.date() == datetime.now().date()


def test_get_watchstock_data_api_rate_limit_exceeded(new_watch_stock, mock_requests_get_api_rate_limit_exceeded):
    """
    GIVEN a monkeypatched (API rate limit exceeded) version of requests.get()
    WHEN the analysis data for the WatchStock object is retrieved
    THEN check that the analysis data is not returned
    """
    new_watch_stock.retrieve_stock_analysis_data()
    assert new_watch_stock.stock_symbol == 'COST'
    assert new_watch_stock.company_name is None
    assert new_watch_stock.current_share_price == 0
    assert new_watch_stock.current_share_price_date is None
    assert new_watch_stock.fiftytwo_week_low == 0
    assert new_watch_stock.fiftytwo_week_high == 0
    assert new_watch_stock.market_cap is None
    assert new_watch_stock.dividend_per_share == 0
    assert new_watch_stock.pe_ratio == 0
    assert new_watch_stock.peg_ratio == 0
    assert new_watch_stock.profit_margin == 0
    assert new_watch_stock.beta == 0
    assert new_watch_stock.price_to_book_ratio == 0
    assert new_watch_stock.stock_data_date is None


def test_get_watchstock_data_failure(new_watch_stock, mock_requests_get_failure):
    """
    GIVEN a monkeypatched (failure) version of requests.get()
    WHEN the analysis data for the WatchStock object is retrieved
    THEN check that the analysis data is not returned
    """
    new_watch_stock.retrieve_stock_analysis_data()
    assert new_watch_stock.stock_symbol == 'COST'
    assert new_watch_stock.company_name is None
    assert new_watch_stock.current_share_price == 0
    assert new_watch_stock.current_share_price_date is None
    assert new_watch_stock.fiftytwo_week_low == 0
    assert new_watch_stock.fiftytwo_week_high == 0
    assert new_watch_stock.market_cap is None
    assert new_watch_stock.dividend_per_share == 0
    assert new_watch_stock.pe_ratio == 0
    assert new_watch_stock.peg_ratio == 0
    assert new_watch_stock.profit_margin == 0
    assert new_watch_stock.beta == 0
    assert new_watch_stock.price_to_book_ratio == 0
    assert new_watch_stock.stock_data_date is None


def test_update_stock_no_changes(new_stock_updated):
    """
    GIVEN an initialized Stock object
    WHEN the stock data is updated but no fields are different
    THEN check that the stock data is unchanged
    """
    new_stock_updated.update(number_of_shares='', purchase_price='', purchase_date='')
    assert new_stock_updated.stock_symbol == 'AAPL'
    assert new_stock_updated.number_of_shares == 16
    assert new_stock_updated.purchase_price == 40678  # $406.78 -> integer
    assert new_stock_updated.purchase_date.date() == datetime(2020, 7, 18).date()
    assert new_stock_updated.current_price == 14834  # $148.34 -> integer
    assert new_stock_updated.current_price_date.date() == datetime.now().date()
    assert new_stock_updated.position_value == (14834*16)


def test_update_stock_all_fields_changed(new_stock_updated):
    """
    GIVEN an initialized Stock object
    WHEN the stock data is updated with all fields being changed
    THEN check that the stock data is updated
    """
    new_stock_updated.update(number_of_shares='27',
                             purchase_price='387.98',
                             purchase_date=datetime.fromisoformat('2021-01-08'))
    assert new_stock_updated.stock_symbol == 'AAPL'
    assert new_stock_updated.number_of_shares == 27
    assert new_stock_updated.purchase_price == 38798  # 387.98 -> integer
    assert new_stock_updated.purchase_date.date() == datetime(2021, 1, 8).date()
    assert new_stock_updated.current_price == 14834  # $148.34 -> integer
    assert new_stock_updated.current_price_date.date() == datetime.now().date()
    assert new_stock_updated.position_value == (14834*27)


def test_update_stock_only_number_of_shares_changed(new_stock_updated):
    """
    GIVEN an initialized Stock object
    WHEN the stock data is updated only the number of shares being changed
    THEN check that the stock data is updated
    """
    new_stock_updated.update(number_of_shares='523', purchase_price='', purchase_date='')
    assert new_stock_updated.stock_symbol == 'AAPL'
    assert new_stock_updated.number_of_shares == 523
    assert new_stock_updated.purchase_price == 40678  # $406.78 -> integer
    assert new_stock_updated.purchase_date.date() == datetime(2020, 7, 18).date()
    assert new_stock_updated.current_price == 14834  # $148.34 -> integer
    assert new_stock_updated.current_price_date.date() == datetime.now().date()
    assert new_stock_updated.position_value == (14834*523)


def test_update_stock_only_purchase_price_changed(new_stock_updated):
    """
    GIVEN an initialized Stock object
    WHEN the stock data is updated only the purchase price being changed
    THEN check that the stock data is updated
    """
    new_stock_updated.update(number_of_shares='', purchase_price='564.98', purchase_date='')
    assert new_stock_updated.stock_symbol == 'AAPL'
    assert new_stock_updated.number_of_shares == 16
    assert new_stock_updated.purchase_price == 56498  # $564.98 -> integer
    assert new_stock_updated.purchase_date.date() == datetime(2020, 7, 18).date()
    assert new_stock_updated.current_price == 14834  # $148.34 -> integer
    assert new_stock_updated.current_price_date.date() == datetime.now().date()
    assert new_stock_updated.position_value == (14834*16)


def test_update_stock_only_purchase_date_changed(new_stock_updated):
    """
    GIVEN an initialized Stock object
    WHEN the stock data is updated only the purchase date being changed
    THEN check that the stock data is updated
    """
    new_stock_updated.update(number_of_shares='',
                             purchase_price='',
                             purchase_date=datetime.fromisoformat('2021-02-02'))
    assert new_stock_updated.stock_symbol == 'AAPL'
    assert new_stock_updated.number_of_shares == 16
    assert new_stock_updated.purchase_price == 40678  # $406.78 -> integer
    assert new_stock_updated.purchase_date.date() == datetime(2021, 2, 2).date()
    assert new_stock_updated.current_price == 14834  # $148.34 -> integer
    assert new_stock_updated.current_price_date.date() == datetime.now().date()
    assert new_stock_updated.position_value == (14834*16)
