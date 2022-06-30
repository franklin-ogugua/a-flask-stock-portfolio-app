import pytest
from project import create_app, database
from flask import current_app
from project.models import Stock, User, WatchStock
from datetime import datetime
import requests


# --------------
# Helper Classes
# --------------

class MockSuccessResponseDaily(object):
    def __init__(self, url):
        self.status_code = 200
        self.url = url

    def json(self):
        return {
            'Meta Data': {
                "2. Symbol": "AAPL",
                "3. Last Refreshed": "2020-03-24"
            },
            'Time Series (Daily)': {
                "2020-03-24": {
                    "4. close": "148.3400",
                },
                "2020-03-23": {
                    "4. close": "135.9800",
                }
            }
        }


class MockSuccessResponseWeekly(object):
    def __init__(self, url):
        self.status_code = 200
        self.url = url

    def json(self):
        return {
            'Meta Data': {
                "2. Symbol": "AAPL",
                "3. Last Refreshed": "2020-07-28"
            },
            'Weekly Adjusted Time Series': {
                "2020-07-24": {
                    "4. close": "379.2400",
                },
                "2020-07-17": {
                    "4. close": "362.7600",
                },
                "2020-06-11": {
                    "4. close": "354.3400",
                },
                "2020-02-25": {
                    "4. close": "432.9800",
                }
            }
        }


class MockSuccessResponseOverview(object):
    def __init__(self, url):
        self.status_code = 200
        self.url = url

    def json(self):
        return {
            'Symbol': 'COST',
            'AssetType': 'Common Stock',
            'Name': 'Costco Wholesale Corporation',
            'Currency': 'USD',
            'MarketCapitalization': '160300990464',
            'PERatio': '37.155',
            'PEGRatio': '3.9329',
            'PriceToBookRatio': '5.2343',
            'BookValue': '33.547',
            'DividendPerShare': '2.8',
            'DividendYield': '0.0077',
            'EPS': '9.74',
            'ProfitMargin': '0.2503',
            'QuarterlyEarningsGrowthYOY': '0.379',
            'QuarterlyRevenueGrowthYOY': '0.167',
            'Beta': '0.674',
            '52WeekHigh': '388.07',
            '52WeekLow': '262.6822'
        }


class MockApiRateLimitExceededResponse(object):
    def __init__(self, url):
        self.status_code = 200
        self.url = url

    def json(self):
        return {
            'Note': 'Thank you for using Alpha Vantage! Our standard API call frequency is ' +
                    '5 calls per minute and 500 calls per day.'
        }


class MockFailedResponse(object):
    def __init__(self, url):
        self.status_code = 404
        self.url = url

    def json(self):
        return {'error': 'bad'}


##################
#### Fixtures ####
##################

@pytest.fixture(scope='function')
def new_stock():
    flask_app = create_app()
    flask_app.config.from_object('config.TestingConfig')
    flask_app.extensions['mail'].suppress = True

    # Create a test client using the Flask application configured for testing
    with flask_app.test_client() as testing_client:
        # Establish an application context before accessing the logger and database
        with flask_app.app_context():
            stock = Stock('AAPL', '16', '406.78', 17, datetime(2020, 7, 18))
            yield stock  # this is where the testing happens!


@pytest.fixture(scope='function')
def new_stock_updated(new_stock):
    new_stock.current_price = 14834  # $148.34 -> integer
    new_stock.current_price_date = datetime.now()
    new_stock.position_value = (14834*16)
    return new_stock


@pytest.fixture(scope='module')
def new_user():
    flask_app = create_app()
    flask_app.config.from_object('config.TestingConfig')

    # Establish an application context before creating the User object
    with flask_app.app_context():
        user = User('patrick@email.com', 'FlaskIsAwesome123')
        yield user   # this is where the testing happens!


@pytest.fixture(scope='module')
def test_client():
    flask_app = create_app()
    flask_app.config.from_object('config.TestingConfig')
    flask_app.extensions['mail'].suppress = True

    # Create a test client using the Flask application configured for testing
    with flask_app.test_client() as testing_client:
        # Establish an application context before accessing the logger and database
        with flask_app.app_context():
            flask_app.logger.info('Creating database tables in test_client fixture...')

            # Create the database and the database table(s)
            database.create_all()

        yield testing_client  # this is where the testing happens!

        with flask_app.app_context():
            database.drop_all()


@pytest.fixture(scope='module')
def register_default_user(test_client):
    # Register the default user
    test_client.post('/users/register',
                     data={'email': 'patrick@gmail.com',
                           'password': 'FlaskIsAwesome123'},
                     follow_redirects=True)
    return


@pytest.fixture(scope='function')
def log_in_default_user(test_client, register_default_user):
    # Log in the default user
    test_client.post('/users/login',
                     data={'email': 'patrick@gmail.com',
                           'password': 'FlaskIsAwesome123'},
                     follow_redirects=True)

    yield   # this is where the testing happens!

    # Log out the default user
    test_client.get('/users/logout', follow_redirects=True)


@pytest.fixture(scope='function')
def confirm_email_default_user(test_client, log_in_default_user):
    # Mark the user as having their email address confirmed
    user = User.query.filter_by(email='patrick@gmail.com').first()
    user.email_confirmed = True
    user.email_confirmed_on = datetime(2020, 7, 8)
    database.session.add(user)
    database.session.commit()

    yield user  # this is where the testing happens!

    # Mark the user as not having their email address confirmed (clean up)
    user = User.query.filter_by(email='patrick@gmail.com').first()
    user.email_confirmed = False
    user.email_confirmed_on = None
    database.session.add(user)
    database.session.commit()


@pytest.fixture(scope='function')
def afterwards_reset_default_user_password():
    yield  # this is where the testing happens!

    # Since a test using this fixture could change the password for the default user,
    # reset the password back to the default password
    user = User.query.filter_by(email='patrick@gmail.com').first()
    user.set_password('FlaskIsAwesome123')
    database.session.add(user)
    database.session.commit()


@pytest.fixture(scope='function')
def add_stocks_for_default_user(test_client, log_in_default_user):
    # Add three stocks for the default user
    test_client.post('/add_stock', data={'stock_symbol': 'SAM',
                                         'number_of_shares': '27',
                                         'purchase_price': '301.23',
                                         'purchase_date': '2020-07-01'})
    test_client.post('/add_stock', data={'stock_symbol': 'COST',
                                         'number_of_shares': '76',
                                         'purchase_price': '14.67',
                                         'purchase_date': '2019-05-26'})
    test_client.post('/add_stock', data={'stock_symbol': 'TWTR',
                                         'number_of_shares': '146',
                                         'purchase_price': '34.56',
                                         'purchase_date': '2020-02-03'})
    return


@pytest.fixture(scope='function')
def mock_requests_get_success_daily(monkeypatch):
    # Create a mock for the requests.get() call to prevent making the actual API call
    def mock_get(url):
        return MockSuccessResponseDaily(url)

    url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=MSFT&apikey=demo'
    monkeypatch.setattr(requests, 'get', mock_get)


@pytest.fixture(scope='function')
def mock_requests_get_success_weekly(monkeypatch):
    # Create a mock for the requests.get() call to prevent making the actual API call
    def mock_get(url):
        return MockSuccessResponseWeekly(url)

    url = 'https://www.alphavantage.co/query?function=TIME_SERIES_WEEKLY&symbol=MSFT&apikey=demo'
    monkeypatch.setattr(requests, 'get', mock_get)


@pytest.fixture(scope='function')
def mock_requests_get_success_overview(monkeypatch):
    # Create a mock for the requests.get() call to prevent making the actual API call
    def mock_get(url):
        return MockSuccessResponseOverview(url)

    url = 'https://www.alphavantage.co/query?function=OVERVIEW&symbol=COST&apikey=demo'
    monkeypatch.setattr(requests, 'get', mock_get)


@pytest.fixture(scope='function')
def mock_requests_get_api_rate_limit_exceeded(monkeypatch):
    def mock_get(url):
        return MockApiRateLimitExceededResponse(url)

    url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=MSFT&apikey=demo'
    monkeypatch.setattr(requests, 'get', mock_get)


@pytest.fixture(scope='function')
def mock_requests_get_failure(monkeypatch):
    def mock_get(url):
        return MockFailedResponse(url)

    url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=MSFT&apikey=demo'
    monkeypatch.setattr(requests, 'get', mock_get)


@pytest.fixture(scope='module')
def register_second_user(test_client):
    """Registers the second user using the '/users/register' route."""
    test_client.post('/users/register',
                     data={'email': 'patrick@yahoo.com',
                           'password': 'FlaskIsTheBest987'})


@pytest.fixture(scope='function')
def log_in_second_user(test_client, register_second_user):
    # Log in the user
    test_client.post('/users/login',
                     data={'email': 'patrick@yahoo.com',
                           'password': 'FlaskIsTheBest987'})

    yield   # this is where the testing happens!

    # Log out the user
    test_client.get('/users/logout', follow_redirects=True)


@pytest.fixture(scope='module')
def new_admin_user():
    flask_app = create_app()
    flask_app.config.from_object('config.TestingConfig')

    # Establish an application context before creating the User object
    with flask_app.app_context():
        admin_user = User('patrick_admin@email.com', 'FlaskIsTheBest987', 'Admin')
        yield admin_user   # this is where the testing happens!


@pytest.fixture(scope='function')
def cli_test_runner():
    flask_app = create_app()
    flask_app.config.from_object('config.TestingConfig')
    flask_app.extensions['mail'].suppress = True

    # Create a test client using the Flask application configured for testing
    with flask_app.test_client() as testing_client:
        # Establish an application context before accessing the logger and database
        with flask_app.app_context():
            # Create the database and the database table(s)
            database.create_all()

        yield flask_app.test_cli_runner()  # this is where the CLI testing happens!

        with flask_app.app_context():
            database.drop_all()


@pytest.fixture(scope='module')
def test_client_admin():
    flask_app = create_app()
    flask_app.config.from_object('config.TestingConfig')
    flask_app.extensions['mail'].suppress = True

    # Create a test client using the Flask application configured for testing
    with flask_app.test_client() as testing_client:
        # Establish an application context before accessing the logger and database
        with flask_app.app_context():
            flask_app.logger.info('Creating database tables with an admin user in test_client_admin fixture...')

            # Create the database and the database table(s)
            database.create_all()

            # Create the admin user
            admin_user = User('patrick_admin@gmail.com', 'FlaskIsSuperGreat456', user_type='Admin')
            database.session.add(admin_user)
            database.session.commit()

            # Create the default set of users
            user1 = User('user1@gmail.com', 'FlaskIsGreat1')
            user2 = User('user2@gmail.com', 'FlaskIsGreat2')
            user3 = User('user3@gmail.com', 'FlaskIsGreat3')
            user4 = User('user4@gmail.com', 'FlaskIsGreat4')
            database.session.add(user1)
            database.session.add(user2)
            database.session.add(user3)
            database.session.add(user4)
            database.session.commit()

        yield testing_client  # this is where the testing happens!

        with flask_app.app_context():
            database.drop_all()


@pytest.fixture(scope='function')
def log_in_admin_user(test_client_admin):
    # Log in the admin user
    test_client_admin.post('/users/login',
                     data={'email': 'patrick_admin@gmail.com',
                           'password': 'FlaskIsSuperGreat456'},
                     follow_redirects=True)

    yield   # this is where the testing happens!

    # Log out the default user
    test_client_admin.get('/users/logout', follow_redirects=True)


@pytest.fixture(scope='function')
def log_in_user1(test_client_admin):
    # Log in the default user
    test_client_admin.post('/users/login',
                           data={'email': 'user1@gmail.com',
                                 'password': 'FlaskIsGreat1'},
                           follow_redirects=True)

    yield   # this is where the testing happens!

    # Log out the default user
    test_client_admin.get('/users/logout', follow_redirects=True)


@pytest.fixture(scope='function')
def new_watch_stock():
    watch_stock = WatchStock('COST', 23)
    return watch_stock


@pytest.fixture(scope='function')
def add_watch_stocks_for_default_user(test_client, log_in_default_user):
    # Add three watch stocks for the default user
    test_client.post('/watchlist/add_watch_stock',
                     data={'stock_symbol': 'COST'})
    test_client.post('/watchlist/add_watch_stock',
                     data={'stock_symbol': 'MSFT'})
    test_client.post('/watchlist/add_watch_stock',
                     data={'stock_symbol': 'QCOM'})
    return
