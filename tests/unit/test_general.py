# test that the tests operate in a mock database
def test_mock_database(app):
    assert app.config['MOCK_DB'] == True