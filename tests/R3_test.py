import pytest
from library_service import borrow_book_by_patron, add_book_to_catalog
from conftest import test_setup

def test_borrow_book_valid_input(test_setup):
    """
    Test borrowing a book with valid input
    """
    success, message = borrow_book_by_patron("100000", 1)

    assert success == True
    assert "Successfully borrowed" in message

def test_borrow_book_invalid_patron_id(test_setup):
    """
    Test borrowing a book with invalid patron ID
    """
    # Test borrowing a book with invalid patron ID (not digits)
    success1, message1 = borrow_book_by_patron("Patron ID", 5)

    assert success1 == False
    assert "Invalid patron" in message1

    # Test borrowing a book with invalid patron ID (less than 6 digits)
    success2, message2 = borrow_book_by_patron("12345", 5)

    assert success2 == False
    assert "6 digits" in message2

    # Test borrowing a book with invalid patron ID (more than 6 digits)
    success3, message3 = borrow_book_by_patron("1234567", 5)

    assert success3 == False
    assert "6 digits" in message3

def test_borrow_book_invalid_book_doesnt_exist(test_setup):
    """
    Test borrowing a book that does not exist
    """
    success, message = borrow_book_by_patron("100001", 100)

    assert success == False
    assert "not found" in message

def test_borrow_book_invalid_no_availability(test_setup):
    """
    Test borrowing a book that is not currently available (no available copies)
    """
    success, message = borrow_book_by_patron("100002", 3)

    assert success == False
    assert "not available" in message

def test_borrow_book_invalid_exceeded_borrowing_limit(test_setup):
    """
    Test borrowing a book with patron that has exceeded the maximum borrowing limit of 5 books
    """
    _, _ = add_book_to_catalog("Testing Borrowing Limits", "Test Author", "9876543210987", 10)

    # Borrow 5 books
    _, _ = borrow_book_by_patron("100003", 4)
    _, _ = borrow_book_by_patron("100003", 4)
    _, _ = borrow_book_by_patron("100003", 4)
    _, _ = borrow_book_by_patron("100003", 4)
    _, _ = borrow_book_by_patron("100003", 4)

    # Borrow 6th book --> should return False
    success, message = borrow_book_by_patron("100003", 4)

    # BUG: Patron can borrow up to 6 books because of logic error in borrow_book_by_patron(), which means borrowing the 6th book returns True (hence the AssertionError).
    assert success == False
    assert "maximum borrowing limit" in message

def test_borrow_book_update_available_copies(test_setup):
    """
    Test borrowing a book will update book availability and create a borrow record
    """

    # Borrow book (book_id = 2) twice so that this book no longer has any available copies
    _, _ = borrow_book_by_patron("100004", 2)
    success1, message1 = borrow_book_by_patron("100004", 2)
    
    # Checking to see that the second copy was borrowed successfully
    assert success1 == True
    assert "Successfully borrowed" in message1

    # Borrow same book again, which should return False. Thus showing that book availability is being updated, which means a borrowing record is being record is being created.
    success2, message2 = borrow_book_by_patron("100004", 2)

    assert success2 == False
    assert "not available" in message2
