import pytest
from library_service import calculate_late_fee_for_book
from database import get_db_connection
from datetime import timedelta, datetime
from conftest import test_setup

# Helper function to simulate test conditions
def add_row_to_borrowed_books(patron_id: str, book_id: int, borrow_date: datetime, due_date: datetime) -> None:
    """ 
    Add a row to the borrow_records database. 
    """
    conn = get_db_connection()
    conn.execute('''
    INSERT INTO borrow_records (patron_id, book_id, borrow_date, due_date)
    VALUES (?, ?, ?, ?)
    ''', (
        patron_id, 
        book_id, 
        borrow_date,
        due_date
    ))
    conn.commit()
    conn.close()


def test_late_fee_calculation_less_than_seven_days(test_setup):
    """
    Testing late fee calculation for an overdue book when less than 7 days overdue
    """
    # Add book to database that is 3 days overdue
    add_row_to_borrowed_books(patron_id="111111", book_id=1, borrow_date=datetime.today() - timedelta(days=17), due_date=datetime.today() - timedelta(days=3))

    result = calculate_late_fee_for_book("111111", 1)
    
    # 3 days overdue x $0.50/day for first 7 days = $1.50
    assert result["fee_amount"] == 1.50
    assert result["days_overdue"] == 3

def test_late_fee_calculation_more_than_seven_days(test_setup):
    """
    Testing late fee calculation for an overdue book when more than 7 days overdue but less than 19 days
    """
    # Add book to database that is 8 days overdue
    add_row_to_borrowed_books(patron_id="111112", book_id=1, borrow_date=datetime.today() - timedelta(days=22), due_date=datetime.today() - timedelta(days=8))

    result = calculate_late_fee_for_book("111112", 1)
    
    # (7 x 0.50) + (1 x 1.00) = 4.50
    assert result["fee_amount"] == 4.50
    assert result["days_overdue"] == 8
    
def test_late_fee_calculation_max_fee_for_book(test_setup):
    """
    Testing late fee calculation for an overdue book that has reached its maximum late fee (minimum lateness threshold to trigger this is 19 days) 
    """
    # Add book to database that is 19 days overdue
    add_row_to_borrowed_books(patron_id="111113", book_id=1, borrow_date=datetime.today() - timedelta(days=33), due_date=datetime.today() - timedelta(days=19))

    result = calculate_late_fee_for_book("111113", 1)
    
    # (7 days x 0.50) + (12 days x 1.00) = $15.50 but maximum late fee per book is 15.00
    assert result["fee_amount"] == 15.00
    assert result["days_overdue"] == 19

def test_late_fee_calculation_no_late_books(test_setup):
    """
    Testing late fee calculation when no books are overdue
    """
    # Add book to database that is not overdue
    add_row_to_borrowed_books(patron_id="111114", book_id=1, borrow_date=datetime.today() - timedelta(days=15), due_date=datetime.today() + timedelta(days=1))

    result = calculate_late_fee_for_book("111114", 1)
    
    # 0 days overdue = 0.00
    assert result["fee_amount"] == 0.00
    assert result["days_overdue"] == 0
    