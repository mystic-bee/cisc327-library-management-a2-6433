import pytest
from services.library_service import add_book_to_catalog

from conftest import test_setup

def test_add_book_invalid_total_copies_negative(test_setup):
    """
    Test adding a book with total copies being a negative integer.
    """
    success, message = add_book_to_catalog("Test Negative Copies", "Negative Nathan", "1000000000000", -5)

    assert success == False
    assert "total copies" in message.lower()

def test_add_book_invalid_missing_title(test_setup):
    """
    Test adding a book with missing title.
    """
    success, message = add_book_to_catalog("", "Some Title-less Author", "1000000000100", 8)

    assert success == False
    assert "title is required" in message.lower()

def test_add_book_invalid_title_too_long(test_setup):
    """
    Test adding a book with title having more than 200 characters
    """
    success, message = add_book_to_catalog("Title title title title title title title title title title title title title title title title title title title title title title title title title title title title title titles titles titles titles", "Some Author", "1000000000001", 8)

    assert success == False
    assert "200 characters" in message.lower()

def test_add_book_invalid_missing_author(test_setup):
    """
    Test adding a book with missing author.
    """
    success, message = add_book_to_catalog("No Author", "", "1000000000200", 4)

    assert success == False
    assert "author is required" in message.lower()

def test_add_book_invalid_author_too_long(test_setup):
    """
    Test adding a book with an author having more than 100 characters.
    """
    success, message = add_book_to_catalog("Title 1", "author author author author author author author author author author authors authors authors authors", "1000000000002", 4)

    assert success == False
    assert "100 characters" in message.lower()

def test_add_book_invalid_duplicate_isbn(test_setup):
    """
    Test adding a book with duplicate ISBN (same ISBN, diff author name, title, total copies).
    """

    # Add valid book
    _, _ = add_book_to_catalog("Title 2", "Some Other Author", "1000000000003", 30)

    # Add another book with same isbn
    success, message = add_book_to_catalog("Title 3", "Some Different Author", "1000000000003", 10)

    assert success == False
    assert "ISBN already exists" in message

def test_add_book_invalid_isbn_input_none_type(test_setup):
    """
    Test adding a book with invalid ISBN (None).
    """

    # Add a book with None as ISBN input
    success, message = add_book_to_catalog("Title 4", "Another Author", None, 10)

    assert success == False
    assert "cannot be None" in message

def test_add_book_invalid_isbn_input_whitespace(test_setup):
    """
    Test adding a book with invalid ISBN (whitespace characters).
    """

    # Add a book with whitespace characters as ISBN input
    success, message = add_book_to_catalog("Title 4", "Another Author", "             ", 10)
    
    assert success == False
    assert "cannot have spaces" in message

def test_add_book_invalid_isbn_input_not_digits(test_setup):
    """
    Test adding a book with invalid ISBN (not digits).
    """

    # Add a book with non-digits as ISBN input
    success, message = add_book_to_catalog("Title 4", "Another Author", "abcdefghijklm", 10)
    
    assert success == False
    assert "must be digits" in message
