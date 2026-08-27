import pytest


def test_example():
    """Example test case"""
    assert True


def test_addition():
    """Test basic addition"""
    assert 1 + 1 == 2


def test_subtraction():
    """Test basic subtraction"""
    assert 5 - 3 == 2


def test_multiplication():
    """Test basic multiplication"""
    assert 3 * 4 == 12


def test_division():
    """Test basic division"""
    assert 10 / 2 == 5


def test_string_operations():
    """Test string operations"""
    assert "hello" + " world" == "hello world"
    assert "test".upper() == "TEST"


def test_list_operations():
    """Test list operations"""
    test_list = [1, 2, 3]
    assert len(test_list) == 3
    assert 2 in test_list


def test_exception_handling():
    """Test exception handling"""
    with pytest.raises(ZeroDivisionError):
        result = 1 / 0


@pytest.fixture
def sample_data():
    """Fixture providing sample data"""
    return {"key": "value", "number": 42}


def test_with_fixture(sample_data):
    """Test using fixture"""
    assert sample_data["key"] == "value"
    assert sample_data["number"] == 42