from src.config import Config
import pytest

def test_config_loads():
    # Just checking if class exists and attributes are reachable
    assert hasattr(Config, 'AZURE_OPENAI_API_KEY')

def test_imports():
    from src.search_engine import VisualSearchEngine
    assert VisualSearchEngine is not None
