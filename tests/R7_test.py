"""
Note to the TA:

The return value was not specified by the get_patron_status_report() function. Therefore, I will assume the following response formatting:

{
    'curr_borrowed_books': List[Dict],
        {
            "book_id": int,
            "due_date": datetime
        }
    'total_late_fees_owed': float,
    'num_books_currently_borrowed': int,
    'borrowing_history': List[Dict],
        {
            "book_id": int,
            "borrow_date": datetime,
            "return_date": datetime
        }
}

"""
# Imports
from database import get_db_connection
import pytest
from library_service import get_patron_status_report
from datetime import datetime, timedelta
from conftest import test_setup

# Helper function to simulate test conditions
def add_row_to_borrowed_books(patron_id: str, book_id: int, borrow_date: datetime, due_date: datetime, return_date: datetime | None) -> None:
    """ 
    Add a row to the borrow_records database. 
    """
    conn = get_db_connection()
    conn.execute('''
    INSERT INTO borrow_records (patron_id, book_id, borrow_date, due_date, return_date)
    VALUES (?, ?, ?, ?, ?)
    ''', (
        patron_id, 
        book_id, 
        borrow_date,
        due_date,
        return_date
    ))
    conn.commit()
    conn.close()

# Tests
# def test_get_patron_status_report_standard():
#     """
#     Test patron status for patron with a standard case
#     """
#     # Returned a day late
#     add_row_to_borrowed_books(patron_id="111115", book_id=1, borrow_date=datetime.today() - timedelta(days=42), due_date=datetime.today() - timedelta(days=28), return_date=datetime.today() - timedelta(days=27))

#     # Currently borrowed (not late)
#     add_row_to_borrowed_books(patron_id="111115", book_id=1, borrow_date=datetime.today() - timedelta(days=12), due_date=datetime.today() + timedelta(days=1), return_date=None)

#     result = get_patron_status_report(patron_id="111115")

#     # Test patron status results
#     assert len(result["curr_borrowed_books"]) == 1
#     assert result["curr_borrowed_books"][0]["book_id"] == 12
#     assert result["total_late_fees_owed"] == 0.50
#     assert result["num_books_currently_borrowed"] == 1
#     assert result["borrowing_history"][0]["book_id"] == 1

# def test_get_patron_status_report_no_borrowing_history():
#     """
#     Test patron status for patron with no borrowing history
#     """
#     result = get_patron_status_report(patron_id="111116")

#     # Test patron status results
#     assert len(result["curr_borrowed_books"]) == 0
#     assert result["total_late_fees_owed"] == 0.00
#     assert result["num_books_currently_borrowed"] == 0

# def test_get_patron_status_report_multiple_late_fees():
#     """
#     Test patron status for patron with a borrowing history of multiple overdue books
#     """
#     # Returned 4 day late
#     add_row_to_borrowed_books(patron_id="111117", book_id=1, borrow_date=datetime.today() - timedelta(days=32), due_date=datetime.today() - timedelta(days=18), return_date=datetime.today() - timedelta(days=14))

#     # Returned 20 days late
#     add_row_to_borrowed_books(patron_id="111117", book_id=1, borrow_date=datetime.today() - timedelta(days=36), due_date=datetime.today() - timedelta(days=22), return_date=datetime.today() - timedelta(days=2))

#     # Currently borrowed (not late)
#     add_row_to_borrowed_books(patron_id="111117", book_id=1, borrow_date=datetime.today() - timedelta(days=8), due_date=datetime.today() + timedelta(days=5), return_date=None)

#     result = get_patron_status_report(patron_id="111117")

#     # Test patron status results
#     assert len(result["curr_borrowed_books"]) == 1
#     assert result["total_late_fees_owed"] == 17.00
#     assert result["num_books_currently_borrowed"] == 1

# def test_get_patron_status_report_no_curr_books():
#     """
#     Test patron status for patron with a borrowing history but no currently borrowed books
#     """
#     # Returned on time
#     add_row_to_borrowed_books(patron_id="111118", book_id=1, borrow_date=datetime.today() - timedelta(days=64), due_date=datetime.today() - timedelta(days=50), return_date=datetime.today() - timedelta(days=53))

#     # Returned 11 days late
#     add_row_to_borrowed_books(patron_id="111118", book_id=1, borrow_date=datetime.today() - timedelta(days=33), due_date=datetime.today() - timedelta(days=19), return_date=datetime.today() - timedelta(days=8))

#     result = get_patron_status_report(patron_id="111118")

#     # Test patron status results
#     assert result["total_late_fees_owed"] == 7.50
#     assert result["num_books_currently_borrowed"] == 0

def test_get_patron_status_report_standard(test_setup):
    """
    Test patron status for patron with a standard case
    """
    # Returned a day late
    add_row_to_borrowed_books(patron_id="111115", book_id=1, borrow_date=datetime.today() - timedelta(days=42), due_date=datetime.today() - timedelta(days=28), return_date=datetime.today() - timedelta(days=27))

    # Currently borrowed (not late)
    add_row_to_borrowed_books(patron_id="111115", book_id=1, borrow_date=datetime.today() - timedelta(days=12), due_date=datetime.today() + timedelta(days=1), return_date=None)

    result = get_patron_status_report(patron_id="111115")

    # Test patron status results
    assert len(result["curr_borrowed_books"]) == 1
    assert result["curr_borrowed_books"][0]["book_id"] == 1
    assert result["total_late_fees_owed"] == 0.00
    assert result["num_books_currently_borrowed"] == 1
    assert result["borrowing_history"][0]["book_id"] == 1

def test_get_patron_status_report_no_borrowing_history(test_setup):
    """
    Test patron status for patron with no borrowing history
    """
    result = get_patron_status_report(patron_id="111116")

    # Test patron status results
    assert len(result["curr_borrowed_books"]) == 0
    assert result["total_late_fees_owed"] == 0.00
    assert result["num_books_currently_borrowed"] == 0

def test_get_patron_status_report_multiple_late_fees(test_setup):
    """
    Test patron status for patron with a borrowing history of multiple overdue books
    """
    # Returned 4 day late
    add_row_to_borrowed_books(patron_id="111117", book_id=1, borrow_date=datetime.today() - timedelta(days=32), due_date=datetime.today() - timedelta(days=18), return_date=datetime.today() - timedelta(days=14))

    # Returned 20 days late
    add_row_to_borrowed_books(patron_id="111117", book_id=1, borrow_date=datetime.today() - timedelta(days=36), due_date=datetime.today() - timedelta(days=22), return_date=datetime.today() - timedelta(days=2))

    # Currently borrowed (late)
    add_row_to_borrowed_books(patron_id="111117", book_id=1, borrow_date=datetime.today() - timedelta(days=23), due_date=datetime.today() - timedelta(days=9), return_date=None)

    result = get_patron_status_report(patron_id="111117")

    # Test patron status results
    assert len(result["curr_borrowed_books"]) == 1
    assert result["total_late_fees_owed"] == 5.50
    assert result["num_books_currently_borrowed"] == 1

def test_get_patron_status_report_overdue_books(test_setup):
    """
    Test patron status for patron with current overdue books
    """

    # Add currently borrowed book that is overdue by 9 days
    add_row_to_borrowed_books(patron_id="111118", book_id=1, borrow_date=datetime.today() - timedelta(days=23), due_date=datetime.today() - timedelta(days=9), return_date=None)

    # Add currently borrowed book that is overdue by 30 days
    add_row_to_borrowed_books(patron_id="111118", book_id=2, borrow_date=datetime.today() - timedelta(days=44), due_date=datetime.today() - timedelta(days=30), return_date=None)

    result = get_patron_status_report(patron_id="111118")

    # Test patron status results
    assert result["total_late_fees_owed"] == 20.50
    assert result["num_books_currently_borrowed"] == 2
