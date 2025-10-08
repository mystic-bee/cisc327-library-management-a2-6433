import pytest
from library_service import add_book_to_catalog

def test_add_book_invalid_total_copies_negative():
    """
    Test adding a book with total copies being a negative integer.
    """
    success, message = add_book_to_catalog("Test Negative Copies", "Negative Nathan", "1000000000000", -5)

    assert success == False
    assert "total copies" in message.lower()

def test_add_book_invalid_title_too_long():
    """
    Test adding a book with title having more than 200 characters
    """
    success, message = add_book_to_catalog("Title title title title title title title title title title title title title title title title title title title title title title title title title title title title title titles titles titles titles", "Some Author", "1000000000001", 8)

    assert success == False
    assert "200 characters" in message.lower()

# Test adding an author with more than 100 characters
def test_add_book_invalid_author_too_long():
    """
    Test adding a book with an author having more than 100 characters.
    """
    success, message = add_book_to_catalog("Title 1", "author author author author author author author author author author authors authors authors authors", "1000000000002", 4)

    assert success == False
    assert "100 characters" in message.lower()

# Test adding a duplicate ISBN (same ISBN, diff author name, title, total copies)
def test_add_book_invalid_duplicate_isbn():
    """
    Test adding a book with duplicate ISBN (same ISBN, diff author name, title, total copies).
    """

    # Add valid book
    _, _ = add_book_to_catalog("Title 2", "Some Other Author", "1000000000003", 30)

    # Add another book with same isbn
    success, message = add_book_to_catalog("Title 3", "Some Different Author", "1000000000003", 10)

    assert success == False
    assert "ISBN already exists" in message

def test_add_book_invalid_isbn_input_none_type():
    """
    Test adding a book with invalid ISBN (None).
    """

    # Add a book with None as ISBN input
    success, _ = add_book_to_catalog("Title 4", "Another Author", None, 10)

    # BUG: No error handling for when IBSN input is given None. TypeError is thrown instead.ISBN should only be digits and should be a string.
    assert success == False

def test_add_book_invalid_isbn_input_whitespace():
    """
    Test adding a book with invalid ISBN (whitespace characters).
    """

    # Add a book with whitespace characters as ISBN input
    success, _ = add_book_to_catalog("Title 4", "Another Author", "             ", 10)
    
    # BUG: No error handling for when IBSN input is whitespace characters, so returns True instead. ISBN should only be digits and should be a string.
    assert success == False

def test_add_book_invalid_isbn_input_not_digits():
    """
    Test adding a book with invalid ISBN (not digits).
    """

    # Add a book with non-digits as ISBN input
    success, _ = add_book_to_catalog("Title 4", "Another Author", "abcdefghijklm", 10)
    
    # BUG: No error handling for when IBSN input is non-digit characters, so returns True instead. ISBN should only be digits and should be a string.
    assert success == False

