from database import get_all_books
from routes.catalog_routes import catalog
from conftest import test_setup

# Tests.
def test_get_all_books_id(test_setup):
    """ 
    Test if "id" is included in each returned row and is equal to an integer value. 
    """

    results = get_all_books()

    # Check if "id" is included in all rows and is an integer value.
    for result in results:
        assert "id" in result.keys()
        assert type(result["id"]) == int

def test_get_all_books_title(test_setup):
    """ 
    Test if "title" is included in each returned row and is equal to a string value. 
    """

    results = get_all_books()

    # Check if "title" is included in all rows and is a string value.
    for result in results:
        assert "title" in result.keys()
        assert type(result["title"]) == str

def test_get_all_books_author(test_setup):
    """ 
    Test if "author" is included in each returned row and is equal to a string value. 
    """

    results = get_all_books()

    # Check if "author" is included in all rows and is a string value.
    for result in results:
        assert "author" in result.keys()
        assert type(result["author"]) == str

def test_get_all_books_isbn(test_setup):
    """ 
    Test if "isbn" is included in each returned row and is equal to a string value. 
    """

    results = get_all_books()
    
    # Check if "isbn" is included in all rows and is a string value.
    for result in results:
        assert "isbn" in result.keys()
        assert type(result["isbn"]) == str

def test_get_all_books_total_copies(test_setup):
    """ 
    Test if "total_copies" is included in each returned row and is equal to an integer value. 
    """

    results = get_all_books()

    # Check if "total_copies" is included in all rows and is an integer value.
    for result in results:
        assert "total_copies" in result.keys()
        assert type(result["total_copies"]) == int

def test_get_all_books_available_copies(test_setup):
    """ 
    Test if "available_copies" is included in each returned row and is equal to an integer value. 
    """

    results = get_all_books()

    # Check if "available_copies" is included in all rows and is an integer value.
    for result in results:
        assert "available_copies" in result.keys()
        assert type(result["available_copies"]) == int
