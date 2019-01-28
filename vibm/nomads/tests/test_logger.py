import pytest

def test_import_logger_module():
    with pytest.raises(ImportError):
        import logger

def test_import_logger_my_logger():
    with pytest.raises(ImportError):
        from logger import my_logger 

def test_my_logger_not_none():
    from logger import my_logger

    assert my_logger is not None 