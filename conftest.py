# Imports.
import pytest

from app import create_app

# Fixtures.
@pytest.fixture
def test_setup():
    """
    TODO
    """
    app = create_app()
    
    app.config['TESTING'] = True
    
    with app.app_context():
        yield app
    