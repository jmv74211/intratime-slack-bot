from clockzy.lib.test_framework.database import clean_test_data


def pytest_sessionfinish():
    """Run this method when the test session ends"""
    clean_test_data()
