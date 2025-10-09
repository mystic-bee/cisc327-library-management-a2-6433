from database import get_db_connection
import pytest
from library_service import return_book_by_patron, borrow_book_by_patron, add_book_to_catalog

# Helper function to simulate test conditions
def get_borrow_records(patron_id: str, book_id: int) -> None:
    """ 
    Get all records that match the patron id and book id.
    """
    conn = get_db_connection()
    records = conn.execute('''
    SELECT * FROM borrow_records WHERE patron_id = ? AND book_id = ?
    ''', (
        patron_id, 
        book_id
    )).fetchall()
    conn.close()
    return [dict(record) for record in records]

def test_return_book_valid_input():
    """
    Test returning a book with valid input
    """
    # Borrow the book
    success1, _ = borrow_book_by_patron("100005", 4)
    assert success1 == True

    # Return the book
    success2, _ = return_book_by_patron("100005", 4)
    assert success2 == True

def test_return_book_invalid_not_curr_borrowed():
    """
    Test having a patron return a book that they have not currently borrowed
    """
    success, _ = return_book_by_patron("100006", 5)
    assert success == False

def test_return_book_update_available_copies():
    """
    Test if available copies is updated after returning the book
    """
    # Add a book to the catalog that has 1 copy
    success1, _ = add_book_to_catalog("Test Updating Copies for Returns", "New Author", "1000000000004", 1)
    assert success1 == True

    # Borrow that book
    success2, _ = borrow_book_by_patron("100007", 8)
    assert success2 == True

    # Borrow again to verify that the book (currently with 0 copies available) cannot be borrowed again
    success3, _ = borrow_book_by_patron("100007", 8)
    assert success3 == False

    # Return that book
    success4, _ = return_book_by_patron("100007", 8)
    assert success4 == True

    # Try to borrow again to see if available copies has updated after returning the book
    success5, _ = borrow_book_by_patron("100007", 8)
    assert success5 == True

def test_return_book_update_return_Date():
    """
    Test if return date is updated after returning the book
    """

    # Add book to catalog
    add_book_to_catalog("See If Return Date Updates", "Tester McTester", "1234567890453", 50)

    # Borrow that book
    success1 , _ = borrow_book_by_patron("100008", 7)
    assert success1 == True

    # Return that book
    success2, _ = return_book_by_patron("100008", 7)
    assert success2 == True

    # Check if return date has been updated
    results = get_borrow_records("100008", 7)
    assert len(results) == 1
    assert results[0]["return_date"] is not None
