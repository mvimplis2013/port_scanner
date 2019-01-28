import pytest

def test_logger_module():
    with pytest.raises(ImportError):
        import logger

