import pytest
from services.library_service import borrow_book_by_patron, add_book_to_catalog
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
    # Add 6 books to catalog
    _, _ = add_book_to_catalog("Testing Borrowing Limits 1", "Test Author 1", "1010101010101", 10)
    _, _ = add_book_to_catalog("Testing Borrowing Limits 2", "Test Author 2", "1010101010102", 10)
    _, _ = add_book_to_catalog("Testing Borrowing Limits 3", "Test Author 3", "1010101010103", 10)
    _, _ = add_book_to_catalog("Testing Borrowing Limits 4", "Test Author 4", "1010101010104", 10)
    _, _ = add_book_to_catalog("Testing Borrowing Limits 5", "Test Author 5", "1010101010105", 10)
    _, _ = add_book_to_catalog("Testing Borrowing Limits 6", "Test Author 6", "1010101010106", 10)

    # Borrow 5 books
    _, _ = borrow_book_by_patron("100003", 4)
    _, _ = borrow_book_by_patron("100003", 5)
    _, _ = borrow_book_by_patron("100003", 6)
    _, _ = borrow_book_by_patron("100003", 7)
    _, _ = borrow_book_by_patron("100003", 8)

    # Borrow 6th book --> should return False
    success, message = borrow_book_by_patron("100003", 9)

    assert success == False
    assert "maximum borrowing limit" in message

def test_borrow_book_update_available_copies(test_setup):
    """
    Test borrowing a book will update book availability and create a borrow record
    """
    # Add book with 1 copy
    _, _ = add_book_to_catalog("Copies Copies Copies", "Author Test", "1000000000001", 1)

    # Borrow book with 1 copy so that it no longer has any available copies
    success1, message1 = borrow_book_by_patron("100004", 4)
    
    # Checking to see that the book was borrowed successfully
    assert success1 == True
    assert "Successfully borrowed" in message1

    # Have another patron try to borrow that book with no available copies
    success2, message2 = borrow_book_by_patron("100005", 4)

    assert success2 == False
    assert "not available" in message2

def test_borrow_book_another_copy(test_setup):
    """
    Test borrowing another copy of a book that is already currently borrowed
    """
    # Add a book
    _, _ = add_book_to_catalog("Only One Copy", "Grabby Patty", "1000000000002", 19)

    # Have same patron borrow same book twice
    _, _ = borrow_book_by_patron("100020", 4)
    success1, message1 = borrow_book_by_patron("100020", 4)
    
    # Checking to see that patron is only allowed to borrow one copy at a time
    assert success1 == False
    assert "already borrowed a copy" in message1.lower()
