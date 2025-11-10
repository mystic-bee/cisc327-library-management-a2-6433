import pytest
from unittest.mock import Mock
from services.library_service import pay_late_fees, refund_late_fee_payment, add_book_to_catalog, borrow_book_by_patron, return_book_by_patron
from services.payment_service import PaymentGateway

def test_pay_late_fees_successful_payment(mocker):
    """
    Test successful payment.
    """
    # Stub database functions that return valid values
    mocker.patch("services.library_service.calculate_late_fee_for_book", return_value={"fee_amount": 10.50})
    mocker.patch("database.get_book_by_id", return_value={"title": "The Great Gatsby"})

    mock_gateway = Mock(spec=PaymentGateway)

    # Mocked method in gateway should return successful response
    mock_gateway.process_payment.return_value = (True, "txn_123", "success")
    success, msg, txn = pay_late_fees("123456", 1, mock_gateway)

    # Payment processed successfully through gateway
    assert success == True
    assert "Payment successful" in msg
    assert txn == "txn_123"

    # Verify that method was called with the correct arguments
    mock_gateway.process_payment.assert_called_with(
        patron_id="123456",
        amount=10.50,
        description=f"Late fees for 'The Great Gatsby'"
    )

def test_pay_late_fees_declined_payment(mocker):
    """
    Test when payment is declined by gateway.
    """
    # Stub database functions that return valid values
    mocker.patch("services.library_service.calculate_late_fee_for_book", return_value={"fee_amount": 10.50})
    mocker.patch("database.get_book_by_id", return_value={"title": "The Great Gatsby"})

    mock_gateway = Mock(spec=PaymentGateway)

    # Mocked method in gateway should return unsuccessful response
    mock_gateway.process_payment.return_value = (False, "", "card declined")
    success, msg, txn = pay_late_fees("123456", 1, mock_gateway)

    # Payment processed unsuccessfully through gateway
    assert success == False
    assert "Payment failed" in msg
    assert txn is None

    mock_gateway.process_payment.assert_called_once()

def test_pay_late_fees_invalid_patron_id():
    """
    Test invalid patron ID.
    """
    mock_gateway = Mock(spec=PaymentGateway)

    # Attempt to pay late fee with invalid patron id
    success, msg, txn = pay_late_fees("id123", 1, mock_gateway)

    assert success == False
    assert "Invalid patron ID" in msg
    assert txn is None

    # Verify that gateway is not called
    mock_gateway.process_payment.assert_not_called()

def test_pay_late_fees_zero_late_fees(mocker):
    """
    Test zero late fees.
    """
    # Stub calculate_late_fee_for_book to simulate case when fee_amount is 0
    mocker.patch("services.library_service.calculate_late_fee_for_book", return_value={"fee_amount": 0.0})

    mock_gateway = Mock(spec=PaymentGateway)
    success, msg, txn = pay_late_fees("123456", 1, mock_gateway)

    assert success == False
    assert "No late fees" in msg
    assert txn is None

    # Verify that gateway is not called
    mock_gateway.process_payment.assert_not_called()

def test_pay_late_fees_exception_handling(mocker):
    """
    Test network error exception handling.
    """
    # Stub database functions that return valid values
    mocker.patch("services.library_service.calculate_late_fee_for_book", return_value={"fee_amount": 10.50})
    mocker.patch("database.get_book_by_id", return_value={"title": "The Great Gatsby"})

    mock_gateway = Mock(spec=PaymentGateway)

    # Payment gateway should raise an exception
    mock_gateway.process_payment.side_effect = Exception("network error")
    success, msg, txn = pay_late_fees("123456", 1, mock_gateway)

    assert success == False
    assert "Payment processing error" in msg
    assert txn is None

    mock_gateway.process_payment.assert_called_once()

def test_refund_late_fee_successful_refund():
    """
    Test successful refund.
    """
    mock_gateway = Mock(spec=PaymentGateway)

    # Mocked method in gateway should return successful response
    mock_gateway.refund_payment.return_value = (True, "Refund processed successfully!")

    # Refund valid amount
    success, msg = refund_late_fee_payment("txn_123", 7.0, mock_gateway)

    assert success == True
    assert "Refund processed successfully!" in msg

    # Verify that method was called with the correct arguments
    mock_gateway.refund_payment.assert_called_with("txn_123", 7.0)

def test_refund_late_fee_invalid_transaction_id():
    """
    Test invalid transaction ID rejection.
    """
    mock_gateway = Mock(spec=PaymentGateway)

    # Attempt refund with invalid transaction id
    success, msg = refund_late_fee_payment("", 7.0, mock_gateway)

    assert success == False
    assert "Invalid transaction ID" in msg

    mock_gateway.refund_payment.assert_not_called()

def test_refund_late_fee_invalid_amount_negative():
    """
    Test invalid refund amount (negative).
    """
    mock_gateway = Mock(spec=PaymentGateway)

    # Attempt to refund invalid amount (negative)
    success, msg = refund_late_fee_payment("txn_123", -0.50, mock_gateway)

    assert success == False
    assert "must be greater than 0" in msg

    mock_gateway.refund_payment.assert_not_called()

def test_refund_late_fee_invalid_amount_zero():
    """
    Test invalid refund amount (zero).
    """
    mock_gateway = Mock(spec=PaymentGateway)

    # Attempt to refund invalid amount (0)
    success, msg = refund_late_fee_payment("txn_123", 0.0, mock_gateway)

    assert success == False
    assert "must be greater than 0" in msg

    mock_gateway.refund_payment.assert_not_called()

def test_refund_late_fee_invalid_amount_exceeds_max():
    """
    Test invalid refund amount (exceeds $15 maximum).
    """
    mock_gateway = Mock(spec=PaymentGateway)

    # Attempt to refund invalid amount (over $15)
    success, msg = refund_late_fee_payment("txn_123", 15.50, mock_gateway)

    assert success == False
    assert "exceeds maximum late fee" in msg

    mock_gateway.refund_payment.assert_not_called()


# ============================================================
#               TASK 2.2: CODE COVERAGE TESTING
#                    (payment_service.py)
# ============================================================

def test_initialize_payment_gateway():
    """
    Test initialization of payment gateway.
    """
    gateway = PaymentGateway()

    # Check if correct API key and base url 
    assert gateway.api_key == "test_key_12345"
    assert gateway.base_url == "https://api.payment-gateway.example.com"

def test_process_payment_invalid_amount():
    """
    Test processing a payment with an invalid amount.
    """
    gateway = PaymentGateway()
    # Process payment with invalid amount (0)
    success, txn_id, msg = gateway.process_payment("123456", 0, "Late fees")

    assert success == False
    assert "Invalid amount: must be greater than 0" in msg

def test_process_payment_limit_exceeding_amount():
    """
    Test processing a payment amount that exceeds the limit.
    """
    gateway = PaymentGateway()
    # Process payment with amount above the limit
    success, _, msg = gateway.process_payment("123456", 1001, "Excessive amount")

    assert success == False
    assert "Payment declined: amount exceeds limit" in msg

def test_process_payment_invalid_patron_id():
    """
    Test processing a payment with an invalid patron ID.
    """
    gateway = PaymentGateway()
    # Process payment with invalid patron ID
    success, _, msg = gateway.process_payment("123", 10.0, "Late fees")

    assert success == False
    assert "Invalid patron ID format" in msg

def test_process_payment_successful_payment():
    """
    Test processing a successful payment.
    """
    gateway = PaymentGateway()
    # Process valid payment
    success, txn_id, msg = gateway.process_payment("123456", 6.50, "Late fees")

    assert success == True
    assert txn_id.startswith("txn_") == True
    assert "Payment of $6.50 processed successfully" in msg

def test_refund_payment_invalid_transaction_id():
    """
    Test refund with invalid transaction ID.
    """
    gateway = PaymentGateway()
    # Try refunding with invalid transaction ID
    success, msg = gateway.refund_payment("123txn_", 8.50)

    assert success == False
    assert "Invalid transaction ID" in msg

def test_refund_payment_invalid_refund_amt():
    """
    Test refund with invalid refund amount.
    """
    gateway = PaymentGateway()
    # Try refunding with invalid refund amount (0)
    success, msg = gateway.refund_payment("txn_123", 0.0)

    assert success == False
    assert "Invalid refund amount" in msg

def test_refund_payment_successful_refund():
    """
    Test successful refund.
    """
    gateway = PaymentGateway()
    # Process valid refund
    success, msg = gateway.refund_payment("txn_123", 3.0)

    assert success == True
    assert "Refund of $3.00 processed successfully" in msg

def test_verify_payment_status_invalid_transaction_id():
    """
    Test verifying payment status with an invalid transaction ID.
    """
    gateway = PaymentGateway()
    # Attempt to verify payment status with invalid transaction ID
    status_info = gateway.verify_payment_status("invalid123")

    assert status_info["status"] == "not_found"
    assert status_info["message"] == "Transaction not found"

def test_verify_payment_status_valid_transaction_id(mocker):
    """
    Test verifying payment status with a valid transaction ID.
    """
    gateway = PaymentGateway()

    # Stub specific timestamp for transaction ID
    mocker.patch("time.time", return_value=1762743099.451787)

    transaction_id = "txn_123456_1762743099"
    # Verify payment status with valid transaction ID
    status_info = gateway.verify_payment_status(transaction_id)

    assert status_info["transaction_id"] == transaction_id
    assert status_info["status"] == "completed"
    assert status_info["amount"] == 10.50
    assert status_info["timestamp"] == 1762743099.451787

# ============================================================
#               TASK 2.2: CODE COVERAGE TESTING
#                    (library_service.py)
# ============================================================

def test_pay_late_fees_no_fee_amount(mocker):
    """
    Test paying late fee when no fee is calculated (no fee to pay).
    """
    # Stub late fee calculation returns None
    mocker.patch("services.library_service.calculate_late_fee_for_book", return_value=None)

    mock_gateway = Mock(spec=PaymentGateway)
    # Try paying late fees with no calculated fee amount
    success, msg, txn = pay_late_fees("123456", 1, mock_gateway)

    assert success == False
    assert "Unable to calculate late fees" in msg
    assert txn is None

    # Verify that gateway is not called
    mock_gateway.process_payment.assert_not_called()

def test_pay_late_fees_no_book_found(mocker):
    """
    Test paying late fee when book is not found.
    """
    mocker.patch("services.library_service.calculate_late_fee_for_book", return_value={"fee_amount": 3.0})
    # Stub book not found in the database
    mocker.patch("database.get_book_by_id", return_value=None)

    mock_gateway = Mock(spec=PaymentGateway)
    # Try paying late fees with non-existent book
    success, msg, txn = pay_late_fees("123456", 100, mock_gateway)

    assert success == False
    assert "Book not found" in msg
    assert txn is None

    # Verify that gateway is not called
    mock_gateway.process_payment.assert_not_called()

def test_pay_late_fees_no_gateway(mocker):
    """
    Test paying late fee with no provided payment gateway.
    """
    mocker.patch("services.library_service.calculate_late_fee_for_book", return_value={"fee_amount": 10.50})
    mocker.patch("database.get_book_by_id", return_value={"title": "The Great Gatsby"})

    mock_gateway_instance = Mock(spec=PaymentGateway)
    mock_gateway_instance.process_payment.return_value = (True, "txn_123", "success")
    mock_gateway = mocker.patch("services.library_service.PaymentGateway", return_value=mock_gateway_instance)

    # Attempt to pay late fee without provided gateway
    success, msg, txn = pay_late_fees("123456", 1, None)

    assert success == True
    assert "Payment successful" in msg
    assert txn == "txn_123"

    # Verify that gateway was called once to show new gateway was created
    mock_gateway.assert_called_once()

def test_refund_late_fee_payment_no_gateway(mocker):
    """
    Test refunding late fee with no provided payment gateway.
    """
    mock_gateway_instance = Mock(spec=PaymentGateway)
    mock_gateway_instance.refund_payment.return_value = (True, "Refund processed successfully!")
    mock_gateway = mocker.patch("services.library_service.PaymentGateway", return_value=mock_gateway_instance)

    # Attempt to refund late fee without provided gateway
    success, msg = refund_late_fee_payment("txn_123", 7.0, None)

    assert success == True
    assert "Refund processed successfully" in msg

    # Verify that gateway was called once to show new gateway was created
    mock_gateway.assert_called_once()

def test_refund_late_fee_payment_failed_refund(mocker):
    """
    Test refunding late fee when refund fails.
    """
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.refund_payment.return_value = (False, "denied")

    # Attempt to refund late fee (should fail)
    success, msg = refund_late_fee_payment("txn_123", 7.0, mock_gateway)

    assert success == False
    assert "Refund failed" in msg

    mock_gateway.refund_payment.assert_called_once()

def test_refund_late_fee_payment_exception_handling(mocker):
    """
    Test refunding late fee when exception is raised.
    """
    mock_gateway = Mock(spec=PaymentGateway)
    # Payment gateway should raise an exception
    mock_gateway.refund_payment.side_effect = Exception("network error")
    
    # Try refunding late fee (should throw exception)
    success, msg = refund_late_fee_payment("txn_123", 7.0, mock_gateway)

    assert success == False
    assert "Refund processing error" in msg

    mock_gateway.refund_payment.assert_called_once()

def test_add_book_database_error(mocker):
    """
    R1: Test adding a book when there is a database error
    """
    mocker.patch("services.library_service.get_book_by_isbn", return_value=None)
    # Stub database function to simulate condition that database error gets triggered
    mocker.patch("services.library_service.insert_book", return_value=False)

    # Try adding a book 
    success, msg = add_book_to_catalog("Title Title", "Author Author", "1010101010101", 10)

    assert success == False
    assert "Database error occurred while adding the book" in msg

def test_borrow_book_borrow_success_error(mocker):
    """
    R3: Test borrowing a book when there is a database error while creating borrow record
    """
    mocker.patch("services.library_service.get_book_by_id", return_value={"title": "The Great Gatsby", "available_copies": 3})
    mocker.patch("services.library_service.get_patron_borrowed_books", return_value=[])
    mocker.patch("services.library_service.get_patron_borrow_count", return_value=2)
    # Stub database function to simulate condition where database error gets triggered
    mocker.patch("services.library_service.insert_borrow_record", return_value=False)

    # Try borrowing a book
    success, msg = borrow_book_by_patron("123456", 1)

    assert success == False
    assert "Database error occurred while creating borrow record" in msg

def test_borrow_book_update_availability_error(mocker):
    """
    R3: Test borrowing a book when there is a database error while updating book availability
    """
    mocker.patch("services.library_service.get_book_by_id", return_value={"title": "The Great Gatsby", "available_copies": 3})
    mocker.patch("services.library_service.get_patron_borrowed_books", return_value=[])
    mocker.patch("services.library_service.get_patron_borrow_count", return_value=2)
    mocker.patch("services.library_service.insert_borrow_record", return_value=True)
    # Stub database function to simulate condition where database error gets triggered
    mocker.patch("services.library_service.update_book_availability", return_value=False)

    # Try borrowing a book
    success, msg = borrow_book_by_patron("123456", 1)

    assert success == False
    assert "Database error occurred while updating book availability" in msg

def test_return_book_update_availability_error(mocker):
    """
    R4: Test returning a book when there is a database error while updating book availability
    """
    mocker.patch("services.library_service.get_patron_borrowed_books", return_value=[{"book_id": 3}])
    # Stub database function to simulate condition where database error gets triggered
    mocker.patch("services.library_service.update_book_availability", return_value=False)

    # Try returning a book
    success, msg = return_book_by_patron("123456", 3)

    assert success == False
    assert "Database error occurred while updating book availability" in msg

def test_return_book_record_return_date_error(mocker):
    """
    R4: Test returning a book when there is a database error while updating book return date
    """
    mocker.patch("services.library_service.get_patron_borrowed_books", return_value=[{"book_id": 3}])
    mocker.patch("services.library_service.update_book_availability", return_value=True)
    mocker.patch("services.library_service.calculate_late_fee_for_book", return_value={"fee_amount": 0.0, "days_overdue": 0})
    # Stub database function to simulate condition where database error gets triggered
    mocker.patch("services.library_service.update_borrow_record_return_date", return_value=False)

    # Try returning a book
    success, msg = return_book_by_patron("123456", 3)

    assert success == False
    assert "Database error occurred while updating book return date" in msg
