"""
Library Service Module - Business Logic Functions
Contains all the core business logic for the Library Management System
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from database import (
    get_book_by_id, get_book_by_isbn, get_patron_borrow_count,
    insert_book, insert_borrow_record, update_book_availability,
    update_borrow_record_return_date, get_all_books, get_patron_borrowed_books, get_all_patron_record
)
import re

def add_book_to_catalog(title: str, author: str, isbn: str, total_copies: int) -> Tuple[bool, str]:
    """
    Add a new book to the catalog.
    Implements R1: Book Catalog Management
    
    Args:
        title: Book title (max 200 chars)
        author: Book author (max 100 chars)
        isbn: 13-digit ISBN
        total_copies: Number of copies (positive integer)
        
    Returns:
        tuple: (success: bool, message: str)
    """
    # Input validation
    if not title or not title.strip():
        return False, "Title is required."
    
    if len(title.strip()) > 200:
        return False, "Title must be less than 200 characters."
    
    if not author or not author.strip():
        return False, "Author is required."
    
    if len(author.strip()) > 100:
        return False, "Author must be less than 100 characters."
    
    if isbn is None:
        return False, "ISBN cannot be None. Must only be comprised of digits in a string."
    
    if len(isbn) != 13:
        return False, "ISBN must be exactly 13 digits."
    
    if ' ' in isbn:
        return False, "ISBN cannot have spaces."
    
    if not isbn.isdigit():
        return False, "ISBN must be digits"

    if not isinstance(total_copies, int) or total_copies <= 0:
        return False, "Total copies must be a positive integer."
    
    # Check for duplicate ISBN
    existing = get_book_by_isbn(isbn)
    if existing:
        return False, "A book with this ISBN already exists."
    
    # Insert new book
    success = insert_book(title.strip(), author.strip(), isbn, total_copies, total_copies)
    if success:
        return True, f'Book "{title.strip()}" has been successfully added to the catalog.'
    else:
        return False, "Database error occurred while adding the book."

def borrow_book_by_patron(patron_id: str, book_id: int) -> Tuple[bool, str]:
    """
    Allow a patron to borrow a book.
    Implements R3 as per requirements  
    
    Args:
        patron_id: 6-digit library card ID
        book_id: ID of the book to borrow
        
    Returns:
        tuple: (success: bool, message: str)
    """
    # Validate patron ID
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return False, "Invalid patron ID. Must be exactly 6 digits."
    
    # Check if book exists and is available
    book = get_book_by_id(book_id)
    if not book:
        return False, "Book not found."
    
    if book['available_copies'] <= 0:
        return False, "This book is currently not available."
    
    # Check if patron is trying to borrow a copy of a book that they have currently borrowed
    patron_curr_books = get_patron_borrowed_books(patron_id)
    for curr_book in patron_curr_books:
        if curr_book["book_id"] == book_id:
            return False, "You have already borrowed a copy of this book."
    
    # Check patron's current borrowed books count
    current_borrowed = get_patron_borrow_count(patron_id)
    
    if current_borrowed >= 5:
        return False, "You have reached the maximum borrowing limit of 5 books."
    
    # Create borrow record
    borrow_date = datetime.now()
    due_date = borrow_date + timedelta(days=14)
    
    # Insert borrow record and update availability
    borrow_success = insert_borrow_record(patron_id, book_id, borrow_date, due_date)
    if not borrow_success:
        return False, "Database error occurred while creating borrow record."
    
    availability_success = update_book_availability(book_id, -1)
    if not availability_success:
        return False, "Database error occurred while updating book availability."
    
    return True, f'Successfully borrowed "{book["title"]}". Due date: {due_date.strftime("%Y-%m-%d")}.'

def return_book_by_patron(patron_id: str, book_id: int) -> Tuple[bool, str]:
    """
    Process book return by a patron.
    Implements R4 as per requirements  
    
    Args:
        patron_id: 6-digit library card ID
        book_id: ID of the book to borrow
    
    Returns:
        tuple: (success: bool, message: str)
    """

    # The system shall provide a return interface that includes:
    # - Accepts patron ID and book ID as form parameters
    # - Verifies the book was borrowed by the patron
    # - Updates available copies and records return date
    # - Calculates and displays any late fees owed

    patron_current_books = get_patron_borrowed_books(patron_id)

    borrowed_book = [record for record in patron_current_books if record["book_id"] == book_id]
    if not borrowed_book:
        return False, "You have not currently borrowed this book."
    
    # Update available copies
    availability_success = update_book_availability(book_id, +1)
    if not availability_success:
        return False, "Database error occurred while updating book availability."
    
    # Calculates any late fees owed
    calculate_fee = calculate_late_fee_for_book(patron_id, book_id)
    late_fees = calculate_fee["fee_amount"]
    days_late = calculate_fee["days_overdue"]

    # Update return date
    return_date = datetime.now()
    
    # Record return date
    update_return_date = update_borrow_record_return_date(patron_id, book_id, return_date)
    if not update_return_date:
        return False, "Database error occurred while updating book return date."

    if late_fees == 0.00:
        return True, f'You have successfully returned your book. There are no late fees on this book. Thank you!'
    
    return True, f'You have successfully returned your book. This book is {days_late} days late and you owe ${calculate_fee["fee_amount"]:.2f} in late fees for this book.'

def calculate_late_fee_for_book(patron_id: str, book_id: int) -> Dict:
    """
    Calculate late fees for a specific book.
    Implements R5 as per requirements  
    
    Args:
        patron_id: 6-digit library card ID
        book_id: ID of the book to borrow
    
    Returns:
        dict: {"fee_amount": float, "days_overdue": int}
    """

    # The system shall provide an API endpoint GET `/api/late_fee/<patron_id>/<book_id>` that includes the following.
    # - Calculates late fees for overdue books based on:
    #   - Books due 14 days after borrowing
    #   - $0.50/day for first 7 days overdue
    #   - $1.00/day for each additional day after 7 days
    #   - Maximum $15.00 per book
    # - Returns JSON response with fee amount and days overdue

    patron_current_books = get_patron_borrowed_books(patron_id)

    borrowed_book = [record for record in patron_current_books if record["book_id"] == book_id]

    # Check if no borrowed books
    if not borrowed_book:
        return {"fee_amount": 0.00, "days_overdue": 0}

    for book in borrowed_book:
        overdue_status = book["is_overdue"]

    # Check if book is overdue
    if not overdue_status:
        return {"fee_amount": 0.00, "days_overdue": 0}
    
    today = datetime.now()
    for book in borrowed_book:
        borrow_due_date = book["due_date"]

    # Get number of days overdue
    time_diff = today - borrow_due_date
    num_days_overdue = time_diff.days

    overdue_amt = 0.00

    # $0.50/day for first 7 days overdue
    if num_days_overdue <= 7:
        overdue_amt = num_days_overdue * 0.50
        return {"fee_amount": overdue_amt, "days_overdue": num_days_overdue}
    
    # $1.00/day for each additional day after 7 days
    elif (num_days_overdue > 7):
        overdue_amt = (7 * 0.50) + ((num_days_overdue - 7) * 1.00)

        if overdue_amt < 15.00:
            return {"fee_amount": overdue_amt, "days_overdue": num_days_overdue}
        
        # Maximum $15.00 late fee
        else:
            return {"fee_amount": 15.00, "days_overdue": num_days_overdue}


def search_books_in_catalog(search_term: str, search_type: str) -> List[Dict]:
    """
    Search for books in the catalog.
    Implements R6 as per requirements  
    
    Args:
        search_term: Entered search value
        search_type: title, author, or isbn
    
    Returns:
        List[Dict]: [{"id": int, "title": str, "author": str, "isbn": str, "total_copies": int, "available_copies": int}]
    """

    # The system shall provide search functionality with the following parameters:
    # - `q`: search term
    # - `type`: search type (title, author, isbn)
    # - Support partial matching for title/author (case-insensitive)
    # - Support exact matching for ISBN
    # - Return results in same format as catalog display
    
    all_books = get_all_books()

    search_results = []

    for b in all_books:

        # Support exact matching for isbn
        if search_type == "isbn":
            if "isbn" in b and b["isbn"] == search_term:
                search_results.append(b)
        
        # Support partial matching for title (case-insensitive)
        elif search_type == "title":
            if "title" in b and search_term.lower() in b["title"].lower():
                search_results.append(b)

        # Support partial matching for author (case-insensitive, also added compatibility for partial matching when missing punctuation or spaces, etc.)
        elif search_type == "author":
            if "author" in b and search_term.lower() in b["author"].lower():
                search_results.append(b)

    return search_results

def get_patron_status_report(patron_id: str) -> Dict:
    """
    Get status report for a patron.
    Implements R7 as per requirements  
    
    Args:
        patron_id: 6-digit library card ID
    
    Returns:
        Dict: {
            "curr_borrowed_books": List[Dict]: {
                "book_id": int,
                "title": str,
                "borrow_date": datetime,
                "due_date": datetime
                },

            "total_late_fees_owed": float, 
            
            "num_books_currently_borrowed": int, 
            
            "borrowing_history" List[Dict]: {
                "book_id": int,
                "title": str,
                "return_date": datetime
                }
            }
    """

    # The system shall display patron status for a particular patron that includes the following: 

    # - Currently borrowed books with due dates
    # - Total late fees owed  
    # - Number of books currently borrowed
    # - Borrowing history

    # **Note**: There should be a menu option created for showing the patron status in the main interface

    patron_current_books = get_patron_borrowed_books(patron_id)

    # Currently borrowed books with due dates
    currently_borrowed = []
    for books in patron_current_books:
        currently_borrowed.append({
            "book_id": books.get("book_id"),
            "title": books.get("title"),
            "borrow_date": books.get("borrow_date"),
            "due_date": books.get("due_date")
        })

    # Number of books currently borrowed
    num_currently_borrowed = len(currently_borrowed)

    # Total late fees owed
    book_fees = []
    for id in currently_borrowed:
        book_fees.append(calculate_late_fee_for_book(patron_id, id.get("book_id")))
    
    overdue_fees = []
    for fee_amt in book_fees:
        overdue_fees.append(float(fee_amt.get("fee_amount")))
    
    total_overdue = sum(overdue_fees)

    patron_all_books = get_all_patron_record(patron_id)

    # Borrowing history
    borrowing_history = []
    for item in patron_all_books:
        borrowing_history.append({
            "book_id": item.get("book_id"),
            "title":item.get("title"),
            "return_date": item.get("return_date")
        })

    total_overdue_rounded = round(total_overdue, 2)

    return {
        "curr_borrowed_books": currently_borrowed, 
        "total_late_fees_owed": total_overdue_rounded, 
        "num_books_currently_borrowed": num_currently_borrowed, 
        "borrowing_history": borrowing_history
    }

if __name__ == "__main__":
    return_book_by_patron("111118", 2)